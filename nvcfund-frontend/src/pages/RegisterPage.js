import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useErrorHandler } from '../hooks/useErrorHandler';
import api from '../services/api';
import SecurityManager from '../security/SecurityManager';
import InputValidator from '../security/InputValidator';

const RegisterPage = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const { } = useErrorHandler(); // Available for error handling
  
  const [formData, setFormData] = useState({
    // Account Credentials
    username: '',
    email: '',
    password: '',
    confirm_password: '',
    
    // Personal Information (Required by KYC)
    first_name: '',
    last_name: '',
    middle_name: '',
    date_of_birth: '',
    nationality: '',
    phone_number: '',
    
    // Address Information (Required by KYC)
    address_line1: '',
    address_line2: '',
    city: '',
    state_province: '',
    postal_code: '',
    country: 'US',
    
    // Account Type (Required)
    account_type: 'individual_account',
    
    // Identity Document (Required by KYC)
    identity_document_type: 'passport',
    identity_document_number: '',
    identity_document_expiry: '',
    
    // Legal Consents (Required)
    accept_terms: false,
    accept_privacy: false,
    consent_marketing: false
  });
  
  const [validationErrors, setValidationErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  
  const securityManager = new SecurityManager();
  const inputValidator = new InputValidator();
  
  // Country options (common countries for banking)
  const countries = [
    { code: 'US', name: 'United States' },
    { code: 'CA', name: 'Canada' },
    { code: 'GB', name: 'United Kingdom' },
    { code: 'AU', name: 'Australia' },
    { code: 'DE', name: 'Germany' },
    { code: 'FR', name: 'France' },
    { code: 'IT', name: 'Italy' },
    { code: 'ES', name: 'Spain' },
    { code: 'NL', name: 'Netherlands' },
    { code: 'CH', name: 'Switzerland' },
    { code: 'JP', name: 'Japan' },
    { code: 'SG', name: 'Singapore' }
  ];
  
  // Identity document types
  const documentTypes = [
    { value: 'passport', label: 'Passport' },
    { value: 'national_id', label: 'National ID Card' },
    { value: 'drivers_license', label: 'Driver\'s License' }
  ];
  
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === 'checkbox' ? checked : value;
    
    setFormData(prev => ({ ...prev, [name]: newValue }));
    
    // Clear validation errors for this field
    if (validationErrors[name]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
    
    setError('');
    setSuccess('');
  };
  
  const validateForm = () => {
    const errors = {};
    
    // Username validation
    if (!formData.username) {
      errors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      errors.username = 'Username must be at least 3 characters';
    } else if (!/^[a-zA-Z0-9_]+$/.test(formData.username)) {
      errors.username = 'Username can only contain letters, numbers, and underscores';
    }
    
    // Email validation
    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }
    
    // Password validation
    if (!formData.password) {
      errors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      errors.password = 'Password must be at least 8 characters';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])/.test(formData.password)) {
      errors.password = 'Password must contain uppercase, lowercase, number, and special character';
    }
    
    // Confirm password
    if (formData.password !== formData.confirm_password) {
      errors.confirm_password = 'Passwords do not match';
    }
    
    // Personal information validation
    if (!formData.first_name) errors.first_name = 'First name is required';
    if (!formData.last_name) errors.last_name = 'Last name is required';
    if (!formData.date_of_birth) errors.date_of_birth = 'Date of birth is required';
    if (!formData.nationality) errors.nationality = 'Nationality is required';
    if (!formData.phone_number) errors.phone_number = 'Phone number is required';
    
    // Address validation
    if (!formData.address_line1) errors.address_line1 = 'Address is required';
    if (!formData.city) errors.city = 'City is required';
    if (!formData.state_province) errors.state_province = 'State/Province is required';
    if (!formData.postal_code) errors.postal_code = 'Postal code is required';
    
    // Identity document validation
    if (!formData.identity_document_number) errors.identity_document_number = 'Document number is required';
    if (!formData.identity_document_expiry) errors.identity_document_expiry = 'Document expiry date is required';
    
    // Age validation (18+)
    if (formData.date_of_birth) {
      const today = new Date();
      const birthDate = new Date(formData.date_of_birth);
      const age = today.getFullYear() - birthDate.getFullYear();
      const monthDiff = today.getMonth() - birthDate.getMonth();
      
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
      }
      
      if (age < 18) {
        errors.date_of_birth = 'You must be 18 years or older to register';
      }
    }
    
    // Phone number validation (basic E.164 format)
    if (formData.phone_number && !/^\+[1-9]\d{1,14}$/.test(formData.phone_number)) {
      errors.phone_number = 'Phone number must be in international format (e.g., +1234567890)';
    }
    
    // Legal consents validation
    if (!formData.accept_terms) {
      errors.accept_terms = 'You must accept the terms and conditions';
    }
    if (!formData.accept_privacy) {
      errors.accept_privacy = 'You must accept the privacy policy';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      setError('Please correct the highlighted errors');
      return;
    }
    
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      // Security event reporting
      securityManager.reportSecurityEvent('user_registration_attempt', {
        username: formData.username,
        email: formData.email
      });
      
      const response = await register(formData);
      
      if (response.success) {
        setSuccess('Registration successful! Your account is pending KYC verification. Please check your email for next steps.');
        
        // Clear form
        setFormData({
          username: '', email: '', password: '', confirm_password: '',
          first_name: '', last_name: '', middle_name: '', date_of_birth: '',
          nationality: '', phone_number: '', address_line1: '', address_line2: '',
          city: '', state_province: '', postal_code: '', country: 'US',
          identity_document_type: 'passport', identity_document_number: '',
          identity_document_expiry: '', accept_terms: false, accept_privacy: false,
          consent_marketing: false
        });
        
        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/login', { 
            state: { 
              message: 'Registration successful! Please log in to continue KYC verification.',
              registrationSuccess: true 
            }
          });
        }, 3000);
      } else {
        setError(response.error || 'Registration failed. Please try again.');
      }
    } catch (err) {
      console.error('Registration error:', err);
      setError('Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="container-fluid">
      <div className="row justify-content-center">
        <div className="col-12 col-lg-8 col-xl-6">
          <div className="card shadow-lg border-0">
            <div className="card-header bg-gradient text-center py-4">
              <h2 className="card-title mb-0" style={{ color: '#66ccff' }}>
                Create Your NVC Banking Account
              </h2>
              <p className="mb-0 mt-2" style={{ color: '#e5e7eb' }}>
                Complete KYC verification required for regulatory compliance
              </p>
            </div>
            
            <div className="card-body p-4">
              {error && (
                <div className="alert alert-danger">
                  <i className="fas fa-exclamation-triangle me-2"></i>
                  {error}
                </div>
              )}
              
              {success && (
                <div className="alert alert-success">
                  <i className="fas fa-check-circle me-2"></i>
                  {success}
                </div>
              )}
              
              <form onSubmit={handleSubmit}>
                {/* Account Credentials Section */}
                <div className="mb-4">
                  <h5 className="section-header">Account Credentials</h5>
                  
                  <div className="row">
                    <div className="col-md-6 mb-3">
                      <label htmlFor="username" className="form-label">
                        Username *
                      </label>
                      <input
                        type="text"
                        className={`form-control ${validationErrors.username ? 'is-invalid' : ''}`}
                        id="username"
                        name="username"
                        value={formData.username}
                        onChange={handleInputChange}
                        placeholder="Choose a unique username"
                        required
                      />
                      {validationErrors.username && (
                        <div className="invalid-feedback">{validationErrors.username}</div>
                      )}
                    </div>
                    
                    <div className="col-md-6 mb-3">
                      <label htmlFor="email" className="form-label">
                        Email Address *
                      </label>
                      <input
                        type="email"
                        className={`form-control ${validationErrors.email ? 'is-invalid' : ''}`}
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        placeholder="your.email@example.com"
                        required
                      />
                      {validationErrors.email && (
                        <div className="invalid-feedback">{validationErrors.email}</div>
                      )}
                    </div>
                  </div>
                  
                  <div className="row">
                    <div className="col-md-6 mb-3">
                      <label htmlFor="password" className="form-label">
                        Password *
                      </label>
                      <input
                        type="password"
                        className={`form-control ${validationErrors.password ? 'is-invalid' : ''}`}
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleInputChange}
                        placeholder="Create a strong password"
                        required
                      />
                      {validationErrors.password && (
                        <div className="invalid-feedback">{validationErrors.password}</div>
                      )}
                      <div className="form-text">
                        Must be 8+ characters with uppercase, lowercase, number, and special character
                      </div>
                    </div>
                    
                    <div className="col-md-6 mb-3">
                      <label htmlFor="confirm_password" className="form-label">
                        Confirm Password *
                      </label>
                      <input
                        type="password"
                        className={`form-control ${validationErrors.confirm_password ? 'is-invalid' : ''}`}
                        id="confirm_password"
                        name="confirm_password"
                        value={formData.confirm_password}
                        onChange={handleInputChange}
                        placeholder="Confirm your password"
                        required
                      />
                      {validationErrors.confirm_password && (
                        <div className="invalid-feedback">{validationErrors.confirm_password}</div>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Account Type Selection */}
                <div className="mb-4">
                  <h5 className="section-header">Account Type</h5>
                  <p className="text-muted mb-3">
                    Select the type of account that best describes your banking needs. This affects available services and compliance requirements.
                  </p>
                  
                  <div className="row">
                    <div className="col-12">
                      <div className="row">
                        <div className="col-md-4 mb-3">
                          <div className="form-check account-type-card">
                            <input
                              className="form-check-input"
                              type="radio"
                              name="account_type"
                              id="individual_account"
                              value="individual_account"
                              checked={formData.account_type === 'individual_account'}
                              onChange={handleInputChange}
                            />
                            <label className="form-check-label w-100" htmlFor="individual_account">
                              <div className="card h-100">
                                <div className="card-body text-center">
                                  <i className="fas fa-user fa-2x mb-2 text-primary"></i>
                                  <h6 className="card-title">Individual Account</h6>
                                  <p className="card-text small">
                                    Personal banking for individuals. Standard KYC requirements and personal banking services.
                                  </p>
                                </div>
                              </div>
                            </label>
                          </div>
                        </div>
                        
                        <div className="col-md-4 mb-3">
                          <div className="form-check account-type-card">
                            <input
                              className="form-check-input"
                              type="radio"
                              name="account_type"
                              id="business_client"
                              value="business_client"
                              checked={formData.account_type === 'business_client'}
                              onChange={handleInputChange}
                            />
                            <label className="form-check-label w-100" htmlFor="business_client">
                              <div className="card h-100">
                                <div className="card-body text-center">
                                  <i className="fas fa-building fa-2x mb-2 text-success"></i>
                                  <h6 className="card-title">Business Client</h6>
                                  <p className="card-text small">
                                    Business banking with enhanced compliance, corporate accounts, and commercial services.
                                  </p>
                                </div>
                              </div>
                            </label>
                          </div>
                        </div>
                        
                        <div className="col-md-4 mb-3">
                          <div className="form-check account-type-card">
                            <input
                              className="form-check-input"
                              type="radio"
                              name="account_type"
                              id="partner_program"
                              value="partner_program"
                              checked={formData.account_type === 'partner_program'}
                              onChange={handleInputChange}
                            />
                            <label className="form-check-label w-100" htmlFor="partner_program">
                              <div className="card h-100">
                                <div className="card-body text-center">
                                  <i className="fas fa-handshake fa-2x mb-2 text-warning"></i>
                                  <h6 className="card-title">Partner Program</h6>
                                  <p className="card-text small">
                                    Institutional partnerships with specialized compliance and exclusive services.
                                  </p>
                                </div>
                              </div>
                            </label>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Personal Information Section */}
                <div className="mb-4">
                  <h5 className="section-header">Personal Information</h5>
                  
                  <div className="row">
                    <div className="col-md-4 mb-3">
                      <label htmlFor="first_name" className="form-label">
                        First Name *
                      </label>
                      <input
                        type="text"
                        className={`form-control ${validationErrors.first_name ? 'is-invalid' : ''}`}
                        id="first_name"
                        name="first_name"
                        value={formData.first_name}
                        onChange={handleInputChange}
                        required
                      />
                      {validationErrors.first_name && (
                        <div className="invalid-feedback">{validationErrors.first_name}</div>
                      )}
                    </div>
                    
                    <div className="col-md-4 mb-3">
                      <label htmlFor="middle_name" className="form-label">
                        Middle Name
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        id="middle_name"
                        name="middle_name"
                        value={formData.middle_name}
                        onChange={handleInputChange}
                      />
                    </div>
                    
                    <div className="col-md-4 mb-3">
                      <label htmlFor="last_name" className="form-label">
                        Last Name *
                      </label>
                      <input
                        type="text"
                        className={`form-control ${validationErrors.last_name ? 'is-invalid' : ''}`}
                        id="last_name"
                        name="last_name"
                        value={formData.last_name}
                        onChange={handleInputChange}
                        required
                      />
                      {validationErrors.last_name && (
                        <div className="invalid-feedback">{validationErrors.last_name}</div>
                      )}
                    </div>
                  </div>
                  
                  <div className="row">
                    <div className="col-md-4 mb-3">
                      <label htmlFor="date_of_birth" className="form-label">
                        Date of Birth *
                      </label>
                      <input
                        type="date"
                        className={`form-control ${validationErrors.date_of_birth ? 'is-invalid' : ''}`}
                        id="date_of_birth"
                        name="date_of_birth"
                        value={formData.date_of_birth}
                        onChange={handleInputChange}
                        required
                      />
                      {validationErrors.date_of_birth && (
                        <div className="invalid-feedback">{validationErrors.date_of_birth}</div>
                      )}
                    </div>
                    
                    <div className="col-md-4 mb-3">
                      <label htmlFor="nationality" className="form-label">
                        Nationality *
                      </label>
                      <input
                        type="text"
                        className={`form-control ${validationErrors.nationality ? 'is-invalid' : ''}`}
                        id="nationality"
                        name="nationality"
                        value={formData.nationality}
                        onChange={handleInputChange}
                        placeholder="e.g., American, Canadian"
                        required
                      />
                      {validationErrors.nationality && (
                        <div className="invalid-feedback">{validationErrors.nationality}</div>
                      )}
                    </div>
                    
                    <div className="col-md-4 mb-3">
                      <label htmlFor="phone_number" className="form-label">
                        Phone Number *
                      </label>
                      <input
                        type="tel"
                        className={`form-control ${validationErrors.phone_number ? 'is-invalid' : ''}`}
                        id="phone_number"
                        name="phone_number"
                        value={formData.phone_number}
                        onChange={handleInputChange}
                        placeholder="+1234567890"
                        required
                      />
                      {validationErrors.phone_number && (
                        <div className="invalid-feedback">{validationErrors.phone_number}</div>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Address Information Section */}
                <div className="mb-4">
                  <h5 className="section-header">Address Information</h5>
                  
                  <div className="mb-3">
                    <label htmlFor="address_line1" className="form-label">
                      Address Line 1 *
                    </label>
                    <input
                      type="text"
                      className={`form-control ${validationErrors.address_line1 ? 'is-invalid' : ''}`}
                      id="address_line1"
                      name="address_line1"
                      value={formData.address_line1}
                      onChange={handleInputChange}
                      placeholder="Street address, P.O. Box"
                      required
                    />
                    {validationErrors.address_line1 && (
                      <div className="invalid-feedback">{validationErrors.address_line1}</div>
                    )}
                  </div>
                  
                  <div className="mb-3">
                    <label htmlFor="address_line2" className="form-label">
                      Address Line 2
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="address_line2"
                      name="address_line2"
                      value={formData.address_line2}
                      onChange={handleInputChange}
                      placeholder="Apartment, suite, unit, building, floor, etc."
                    />
                  </div>
                  
                  <div className="row">
                    <div className="col-md-4 mb-3">
                      <label htmlFor="city" className="form-label">
                        City *
                      </label>
                      <input
                        type="text"
                        className={`form-control ${validationErrors.city ? 'is-invalid' : ''}`}
                        id="city"
                        name="city"
                        value={formData.city}
                        onChange={handleInputChange}
                        required
                      />
                      {validationErrors.city && (
                        <div className="invalid-feedback">{validationErrors.city}</div>
                      )}
                    </div>
                    
                    <div className="col-md-4 mb-3">
                      <label htmlFor="state_province" className="form-label">
                        State/Province *
                      </label>
                      <input
                        type="text"
                        className={`form-control ${validationErrors.state_province ? 'is-invalid' : ''}`}
                        id="state_province"
                        name="state_province"
                        value={formData.state_province}
                        onChange={handleInputChange}
                        required
                      />
                      {validationErrors.state_province && (
                        <div className="invalid-feedback">{validationErrors.state_province}</div>
                      )}
                    </div>
                    
                    <div className="col-md-4 mb-3">
                      <label htmlFor="postal_code" className="form-label">
                        Postal Code *
                      </label>
                      <input
                        type="text"
                        className={`form-control ${validationErrors.postal_code ? 'is-invalid' : ''}`}
                        id="postal_code"
                        name="postal_code"
                        value={formData.postal_code}
                        onChange={handleInputChange}
                        required
                      />
                      {validationErrors.postal_code && (
                        <div className="invalid-feedback">{validationErrors.postal_code}</div>
                      )}
                    </div>
                  </div>
                  
                  <div className="mb-3">
                    <label htmlFor="country" className="form-label">
                      Country *
                    </label>
                    <select
                      className="form-control"
                      id="country"
                      name="country"
                      value={formData.country}
                      onChange={handleInputChange}
                      required
                    >
                      {countries.map(country => (
                        <option key={country.code} value={country.code}>
                          {country.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                
                {/* Identity Document Section */}
                <div className="mb-4">
                  <h5 className="section-header">Identity Document</h5>
                  
                  <div className="row">
                    <div className="col-md-4 mb-3">
                      <label htmlFor="identity_document_type" className="form-label">
                        Document Type *
                      </label>
                      <select
                        className="form-control"
                        id="identity_document_type"
                        name="identity_document_type"
                        value={formData.identity_document_type}
                        onChange={handleInputChange}
                        required
                      >
                        {documentTypes.map(doc => (
                          <option key={doc.value} value={doc.value}>
                            {doc.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    
                    <div className="col-md-4 mb-3">
                      <label htmlFor="identity_document_number" className="form-label">
                        Document Number *
                      </label>
                      <input
                        type="text"
                        className={`form-control ${validationErrors.identity_document_number ? 'is-invalid' : ''}`}
                        id="identity_document_number"
                        name="identity_document_number"
                        value={formData.identity_document_number}
                        onChange={handleInputChange}
                        placeholder="Document identification number"
                        required
                      />
                      {validationErrors.identity_document_number && (
                        <div className="invalid-feedback">{validationErrors.identity_document_number}</div>
                      )}
                    </div>
                    
                    <div className="col-md-4 mb-3">
                      <label htmlFor="identity_document_expiry" className="form-label">
                        Document Expiry *
                      </label>
                      <input
                        type="date"
                        className={`form-control ${validationErrors.identity_document_expiry ? 'is-invalid' : ''}`}
                        id="identity_document_expiry"
                        name="identity_document_expiry"
                        value={formData.identity_document_expiry}
                        onChange={handleInputChange}
                        required
                      />
                      {validationErrors.identity_document_expiry && (
                        <div className="invalid-feedback">{validationErrors.identity_document_expiry}</div>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Legal Consents Section */}
                <div className="mb-4">
                  <h5 className="section-header">Legal Consents</h5>
                  
                  <div className="form-check mb-3">
                    <input
                      className={`form-check-input ${validationErrors.accept_terms ? 'is-invalid' : ''}`}
                      type="checkbox"
                      id="accept_terms"
                      name="accept_terms"
                      checked={formData.accept_terms}
                      onChange={handleInputChange}
                      required
                    />
                    <label className="form-check-label" htmlFor="accept_terms">
                      I accept the <Link to="/terms" target="_blank">Terms and Conditions</Link> *
                    </label>
                    {validationErrors.accept_terms && (
                      <div className="invalid-feedback d-block">{validationErrors.accept_terms}</div>
                    )}
                  </div>
                  
                  <div className="form-check mb-3">
                    <input
                      className={`form-check-input ${validationErrors.accept_privacy ? 'is-invalid' : ''}`}
                      type="checkbox"
                      id="accept_privacy"
                      name="accept_privacy"
                      checked={formData.accept_privacy}
                      onChange={handleInputChange}
                      required
                    />
                    <label className="form-check-label" htmlFor="accept_privacy">
                      I accept the <Link to="/privacy" target="_blank">Privacy Policy</Link> *
                    </label>
                    {validationErrors.accept_privacy && (
                      <div className="invalid-feedback d-block">{validationErrors.accept_privacy}</div>
                    )}
                  </div>
                  
                  <div className="form-check mb-3">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      id="consent_marketing"
                      name="consent_marketing"
                      checked={formData.consent_marketing}
                      onChange={handleInputChange}
                    />
                    <label className="form-check-label" htmlFor="consent_marketing">
                      I consent to receiving marketing communications (optional)
                    </label>
                  </div>
                  
                  <div className="alert alert-info">
                    <i className="fas fa-info-circle me-2"></i>
                    <strong>KYC Verification Required:</strong> Your account will be created but remain inactive 
                    until you complete the KYC verification process, including document upload and identity verification.
                  </div>
                </div>
                
                <div className="d-grid gap-2">
                  <button
                    type="submit"
                    className="btn btn-primary btn-lg"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                        Creating Account...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-user-plus me-2"></i>
                        Create Account
                      </>
                    )}
                  </button>
                  
                  <Link to="/login" className="btn btn-outline-secondary">
                    <i className="fas fa-sign-in-alt me-2"></i>
                    Already have an account? Sign In
                  </Link>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;