import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const HomePage = () => {
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return <AuthenticatedHome />;
  }

  return <PublicHome />;
};

const PublicHome = () => {
  return (
    <div className="main-content">
      {/* Hero Section */}
      <div className="hero-section text-white py-5 mb-5 rounded">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-6">
              <h1 className="display-4 fw-bold mb-4 text-gradient">
                NVC Banking Platform
              </h1>
              <p className="lead mb-4">
                Advanced digital banking with comprehensive security, 
                real-time transactions, and institutional-grade financial services.
              </p>
              <div className="d-flex gap-3 flex-wrap">
                <Link to="/login" className="btn btn-outline-primary btn-lg">
                  <i className="fas fa-sign-in-alt me-2"></i>Sign In
                </Link>
                <Link to="/register" className="btn btn-outline-success btn-lg">
                  <i className="fas fa-user-plus me-2"></i>Open Account
                </Link>
              </div>
            </div>
            <div className="col-lg-6 text-center">
              <i className="fas fa-university" style={{ fontSize: '8rem', opacity: '0.7' }}></i>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="container py-4">
        <div className="row">
          <div className="col-md-4 mb-4">
            <div className="card h-100 dashboard-card">
              <div className="card-body text-center">
                <i className="fas fa-shield-alt fa-3x text-success mb-3"></i>
                <h5 className="card-title">Enterprise Security</h5>
                <p className="card-text">
                  Bank-grade security with multi-factor authentication,
                  fraud detection, and real-time monitoring.
                </p>
              </div>
            </div>
          </div>
          
          <div className="col-md-4 mb-4">
            <div className="card h-100 dashboard-card">
              <div className="card-body text-center">
                <i className="fas fa-coins fa-3x text-warning mb-3"></i>
                <h5 className="card-title">NVCT Digital Assets</h5>
                <p className="card-text">
                  NVCT stablecoin integration with blockchain technology
                  for transparent and secure transactions.
                </p>
              </div>
            </div>
          </div>
          
          <div className="col-md-4 mb-4">
            <div className="card h-100 dashboard-card">
              <div className="card-body text-center">
                <i className="fas fa-chart-line fa-3x text-info mb-3"></i>
                <h5 className="card-title">Advanced Analytics</h5>
                <p className="card-text">
                  AI-powered insights, risk assessment, and personalized
                  financial recommendations.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Additional Features */}
        <div className="row mt-4">
          <div className="col-md-6 mb-4">
            <div className="card dashboard-card">
              <div className="card-header">
                <h5 className="mb-0">
                  <i className="fas fa-globe me-2"></i>
                  Global Banking Services
                </h5>
              </div>
              <div className="card-body">
                <ul className="list-unstyled">
                  <li><i className="fas fa-check text-success me-2"></i>International Wire Transfers</li>
                  <li><i className="fas fa-check text-success me-2"></i>Multi-Currency Accounts</li>
                  <li><i className="fas fa-check text-success me-2"></i>Correspondent Banking Network</li>
                  <li><i className="fas fa-check text-success me-2"></i>Trade Finance Solutions</li>
                </ul>
              </div>
            </div>
          </div>
          
          <div className="col-md-6 mb-4">
            <div className="card dashboard-card">
              <div className="card-header">
                <h5 className="mb-0">
                  <i className="fas fa-cog me-2"></i>
                  Advanced Technology
                </h5>
              </div>
              <div className="card-body">
                <ul className="list-unstyled">
                  <li><i className="fas fa-check text-success me-2"></i>Blockchain Infrastructure</li>
                  <li><i className="fas fa-check text-success me-2"></i>Real-time Risk Management</li>
                  <li><i className="fas fa-check text-success me-2"></i>AI-Powered Fraud Detection</li>
                  <li><i className="fas fa-check text-success me-2"></i>Quantum-Safe Encryption</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const AuthenticatedHome = () => {
  const { getUserDisplayName, getUserRoleDisplay } = useAuth();
  
  return (
    <div className="main-content">
      <div className="container py-4">
        <div className="row">
          <div className="col-12 mb-4">
            <h2>Welcome back, {getUserDisplayName()}!</h2>
            <p className="text-muted">{getUserRoleDisplay()} - NVC Banking Platform</p>
          </div>
        </div>
        
        {/* Quick Action Cards */}
        <div className="row">
          <div className="col-md-3 mb-4">
            <div className="card dashboard-card">
              <div className="card-body text-center">
                <i className="fas fa-chart-line fa-2x text-primary mb-2"></i>
                <h6>Dashboard</h6>
                <Link to="/dashboard" className="btn btn-outline-primary btn-sm mt-2">
                  View Details
                </Link>
              </div>
            </div>
          </div>
          
          <div className="col-md-3 mb-4">
            <div className="card dashboard-card">
              <div className="card-body text-center">
                <i className="fas fa-university fa-2x text-success mb-2"></i>
                <h6>Accounts</h6>
                <Link to="/accounts" className="btn btn-outline-success btn-sm mt-2">
                  View Accounts
                </Link>
              </div>
            </div>
          </div>
          
          <div className="col-md-3 mb-4">
            <div className="card dashboard-card">
              <div className="card-body text-center">
                <i className="fas fa-exchange-alt fa-2x text-info mb-2"></i>
                <h6>Transfer</h6>
                <Link to="/transfer" className="btn btn-outline-info btn-sm mt-2">
                  Send Money
                </Link>
              </div>
            </div>
          </div>
          
          <div className="col-md-3 mb-4">
            <div className="card dashboard-card">
              <div className="card-body text-center">
                <i className="fas fa-history fa-2x text-warning mb-2"></i>
                <h6>Transactions</h6>
                <Link to="/transactions" className="btn btn-outline-warning btn-sm mt-2">
                  View History
                </Link>
              </div>
            </div>
          </div>
        </div>
        
        {/* Additional Dashboard Content */}
        <div className="row">
          <div className="col-md-8">
            <div className="card dashboard-card">
              <div className="card-header">
                <h5 className="mb-0">Quick Actions</h5>
              </div>
              <div className="card-body">
                <div className="row">
                  <div className="col-md-6 mb-2">
                    <Link to="/transfer" className="btn btn-outline-primary w-100">
                      <i className="fas fa-paper-plane me-2"></i>Send Money
                    </Link>
                  </div>
                  <div className="col-md-6 mb-2">
                    <Link to="/accounts" className="btn btn-outline-success w-100">
                      <i className="fas fa-plus me-2"></i>Add Account
                    </Link>
                  </div>
                  <div className="col-md-6 mb-2">
                    <Link to="/profile" className="btn btn-outline-info w-100">
                      <i className="fas fa-user me-2"></i>Update Profile
                    </Link>
                  </div>
                  <div className="col-md-6 mb-2">
                    <Link to="/transactions" className="btn btn-outline-warning w-100">
                      <i className="fas fa-download me-2"></i>Download Statement
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="col-md-4">
            <div className="card dashboard-card">
              <div className="card-header">
                <h5 className="mb-0">Account Status</h5>
              </div>
              <div className="card-body">
                <div className="mb-3">
                  <div className="d-flex justify-content-between">
                    <span>Account Verified</span>
                    <i className="fas fa-check-circle text-success"></i>
                  </div>
                </div>
                <div className="mb-3">
                  <div className="d-flex justify-content-between">
                    <span>Security Level</span>
                    <span className="badge bg-success">High</span>
                  </div>
                </div>
                <div className="mb-3">
                  <div className="d-flex justify-content-between">
                    <span>2FA Enabled</span>
                    <i className="fas fa-shield-alt text-primary"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;