import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { securityManager } from '../security/SecurityManager';
import { inputValidator } from '../security/InputValidator';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    remember: false
  });
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});
  const [isBlocked, setIsBlocked] = useState(false);
  const [deviceFingerprint] = useState(() => securityManager.generateDeviceFingerprint());
  
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Clear previous validation errors
    setValidationErrors({});
    
    // Validate inputs using security manager
    const validation = inputValidator.validateLoginForm(formData.username, formData.password);
    
    if (!inputValidator.isFormValid(validation)) {
      setValidationErrors(validation);
      if (window.showNotification) {
        window.showNotification('error', 'Please correct the validation errors');
      }
      return;
    }

    // Check rate limiting
    const rateLimitCheck = securityManager.checkRateLimit('login_attempt', 5, 300000); // 5 attempts per 5 minutes
    if (!rateLimitCheck.allowed) {
      setIsBlocked(true);
      if (window.showNotification) {
        window.showNotification('error', `Too many login attempts. Try again in ${rateLimitCheck.retryAfter} seconds.`);
      }
      return;
    }

    // Check if user has exceeded failed login attempts before attempting login
    const failedAttempts = JSON.parse(localStorage.getItem(`failed_login_${formData.username}`) || '[]');
    const recentFailedAttempts = failedAttempts.filter(time => Date.now() - time < 3600000); // Last hour
    if (recentFailedAttempts.length >= 3) {
      setIsBlocked(true);
      if (window.showNotification) {
        window.showNotification('error', 'Account temporarily blocked due to multiple failed login attempts.');
      }
      return;
    }

    setLoading(true);

    try {
      const result = await login(formData.username, formData.password);
      
      if (result.success) {
        // Clear failed login attempts on success
        securityManager.clearFailedLoginAttempts(formData.username);
        
        // Log successful login with device fingerprint
        securityManager.reportSuspiciousActivity('successful_login', {
          username: formData.username,
          deviceFingerprint,
          timestamp: new Date().toISOString()
        });
        
        if (window.showNotification) {
          window.showNotification('success', `Welcome back, ${result.user.first_name || result.user.username}!`);
        }
        navigate('/dashboard');
      } else {
        // Track failed login attempt
        securityManager.trackFailedLogin(formData.username);
        
        if (window.showNotification) {
          window.showNotification('error', result.error || 'Login failed');
        }
      }
    } catch (error) {
      console.error('Login error:', error);
      
      // Track failed login attempt
      securityManager.trackFailedLogin(formData.username);
      
      if (window.showNotification) {
        window.showNotification('error', 'Connection error. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="main-content">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-md-6 col-lg-4">
            <div className="card dashboard-card shadow mt-5">
              <div className="card-header text-center">
                <h4 className="mb-0">
                  <i className="fas fa-university me-2"></i>NVC Banking Login
                </h4>
              </div>
              <div className="card-body p-4">
                <form onSubmit={handleSubmit}>
                  <div className="mb-3">
                    <label htmlFor="username" className="form-label">Username</label>
                    <div className="input-group">
                      <span className="input-group-text">
                        <i className="fas fa-user"></i>
                      </span>
                      <input
                        type="text"
                        className="form-control"
                        id="username"
                        name="username"
                        value={formData.username}
                        onChange={handleChange}
                        required
                        autoComplete="username"
                        disabled={loading}
                      />
                    </div>
                    {validationErrors.username && !validationErrors.username.isValid && (
                      <div className="invalid-feedback d-block">
                        {validationErrors.username.errors.map((error, index) => (
                          <div key={index}>{error}</div>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  <div className="mb-3">
                    <label htmlFor="password" className="form-label">Password</label>
                    <div className="input-group">
                      <span className="input-group-text">
                        <i className="fas fa-lock"></i>
                      </span>
                      <input
                        type={showPassword ? 'text' : 'password'}
                        className="form-control"
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        required
                        autoComplete="current-password"
                        disabled={loading}
                      />
                      <button
                        className="btn btn-outline-secondary"
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        disabled={loading}
                      >
                        <i className={`fas ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                      </button>
                    </div>
                    {validationErrors.password && !validationErrors.password.isValid && (
                      <div className="invalid-feedback d-block">
                        {validationErrors.password.errors.map((error, index) => (
                          <div key={index}>{error}</div>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  {/* Security Status Indicators */}
                  {(isBlocked || Object.keys(validationErrors).length > 0) && (
                    <div className="alert alert-warning mb-3">
                      <i className="fas fa-shield-alt me-2"></i>
                      <strong>Security Notice:</strong>
                      {isBlocked && <div>Account temporarily blocked due to security concerns.</div>}
                      {Object.keys(validationErrors).length > 0 && (
                        <div>Please correct the validation errors above.</div>
                      )}
                    </div>
                  )}
                  
                  <div className="mb-3 form-check">
                    <input
                      type="checkbox"
                      className="form-check-input"
                      id="remember"
                      name="remember"
                      checked={formData.remember}
                      onChange={handleChange}
                      disabled={loading}
                    />
                    <label className="form-check-label" htmlFor="remember">
                      Remember me
                    </label>
                  </div>
                  
                  <div className="d-grid">
                    <button
                      type="submit"
                      className="btn btn-primary"
                      disabled={loading}
                    >
                      {loading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                          Signing In...
                        </>
                      ) : (
                        <>
                          <i className="fas fa-sign-in-alt me-2"></i>Sign In
                        </>
                      )}
                    </button>
                  </div>
                </form>
                
                <hr className="my-4" />
                
                <div className="text-center">
                  <p className="mb-2">Don't have an account?</p>
                  <Link to="/register" className="btn btn-outline-success">
                    <i className="fas fa-user-plus me-2"></i>Create Account
                  </Link>
                </div>
                
                <div className="text-center mt-3">
                  <small>
                    <a href="#" className="text-decoration-none" onClick={(e) => e.preventDefault()}>
                      Forgot Password?
                    </a>
                  </small>
                </div>
              </div>
              
              <div className="card-footer text-center">
                <small>
                  <i className="fas fa-shield-alt me-1 text-success"></i>
                  Secured with 256-bit SSL encryption
                </small>
              </div>
            </div>
            
            {/* Demo credentials info */}
            <div className="card dashboard-card mt-3">
              <div className="card-body">
                <h6 className="card-title">Demo Access</h6>
                <p className="card-text small mb-2">
                  <strong>Admin:</strong> username: uncode, password: SecureBank2024!
                </p>
                <p className="card-text small mb-0">
                  <strong>User:</strong> Create a new account or use existing credentials
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;