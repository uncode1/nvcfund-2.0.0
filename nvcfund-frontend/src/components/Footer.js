import React from 'react';

const Footer = () => {
  return (
    <footer className="footer bg-dark text-light py-4 mt-auto">
      <div className="container">
        <div className="row">
          <div className="col-md-6">
            <h5>
              <i className="fas fa-university me-2"></i>
              NVC Banking Platform
            </h5>
            <p className="mb-0">Advanced digital banking with enterprise security</p>
            <p className="small text-muted mt-2">
              Blockchain-enabled financial infrastructure with comprehensive security
            </p>
          </div>
          <div className="col-md-6 text-md-end">
            <div className="mb-2">
              <i className="fas fa-shield-alt me-2 text-success"></i>
              <span className="text-success">Bank-grade Security</span>
            </div>
            <div className="mb-2">
              <i className="fas fa-lock me-2 text-info"></i>
              <span className="text-info">SSL Encrypted</span>
            </div>
            <div className="mb-2">
              <i className="fas fa-certificate me-2 text-warning"></i>
              <span className="text-warning">FDIC Insured</span>
            </div>
            <div>
              <i className="fas fa-coins me-2 text-primary"></i>
              <span className="text-primary">NVCT Powered</span>
            </div>
          </div>
        </div>
        
        <hr className="my-3" />
        
        <div className="row align-items-center">
          <div className="col-md-6">
            <div className="d-flex flex-wrap gap-3">
              <a href="/privacy" className="text-light text-decoration-none small">
                Privacy Policy
              </a>
              <a href="/terms" className="text-light text-decoration-none small">
                Terms of Service
              </a>
              <a href="/security" className="text-light text-decoration-none small">
                Security Center
              </a>
              <a href="/support" className="text-light text-decoration-none small">
                Contact Support
              </a>
            </div>
          </div>
          <div className="col-md-6 text-md-end">
            <small className="text-muted">
              &copy; 2025 NVC Banking Platform. All rights reserved.
            </small>
          </div>
        </div>
        
        <div className="row mt-3">
          <div className="col-12 text-center">
            <div className="d-flex justify-content-center gap-3">
              <span className="badge bg-success">
                <i className="fas fa-check-circle me-1"></i>SOC 2 Compliant
              </span>
              <span className="badge bg-info">
                <i className="fas fa-shield-alt me-1"></i>ISO 27001 Certified
              </span>
              <span className="badge bg-warning">
                <i className="fas fa-credit-card me-1"></i>PCI DSS Level 1
              </span>
              <span className="badge bg-primary">
                <i className="fas fa-globe me-1"></i>Global Banking Standards
              </span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;