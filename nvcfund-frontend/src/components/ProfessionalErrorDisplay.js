import React from 'react';

/**
 * Professional Error Display Component
 * Shows user-friendly error messages without exposing technical details
 */
const ProfessionalErrorDisplay = ({ 
  title = "Service Temporarily Unavailable",
  message = "We are experiencing a brief service interruption. Please try again or contact support if the problem persists.",
  onRetry = null,
  showContactInfo = true 
}) => {
  
  const handleReload = () => {
    window.location.reload();
  };

  const handleGoHome = () => {
    window.location.href = '/dashboard';
  };

  return (
    <div className="container-fluid py-5">
      <div className="row justify-content-center">
        <div className="col-md-8 col-lg-6">
          <div className="card shadow border-0">
            <div className="card-body text-center py-5">
              <div className="mb-4">
                <i className="fas fa-shield-alt fa-4x text-warning"></i>
              </div>
              
              <h3 className="mb-3 text-dark">{title}</h3>
              
              <p className="text-muted mb-4 lead">
                {message}
              </p>
              
              <div className="alert alert-light border mb-4">
                <div className="d-flex align-items-center justify-content-center">
                  <i className="fas fa-info-circle text-info me-2"></i>
                  <small className="text-muted mb-0">
                    Our technical team has been automatically notified.
                  </small>
                </div>
              </div>
              
              <div className="d-flex flex-column flex-md-row gap-2 justify-content-center mb-4">
                {onRetry && (
                  <button 
                    className="btn btn-primary px-4"
                    onClick={onRetry}
                  >
                    <i className="fas fa-redo me-2"></i>
                    Try Again
                  </button>
                )}
                
                <button 
                  className="btn btn-primary px-4"
                  onClick={handleReload}
                >
                  <i className="fas fa-redo me-2"></i>
                  Refresh Page
                </button>
                
                <button 
                  className="btn btn-outline-secondary px-4"
                  onClick={handleGoHome}
                >
                  <i className="fas fa-home me-2"></i>
                  Return to Dashboard
                </button>
              </div>
              
              {showContactInfo && (
                <div className="mt-4 pt-4 border-top">
                  <h6 className="text-muted mb-3">Need Immediate Assistance?</h6>
                  <div className="d-flex flex-column flex-md-row gap-2 justify-content-center">
                    <a href="mailto:support@nvcbank.com" className="btn btn-outline-secondary btn-sm">
                      <i className="fas fa-envelope me-1"></i>
                      Email Support
                    </a>
                    <a href="tel:1-800-NVC-BANK" className="btn btn-outline-secondary btn-sm">
                      <i className="fas fa-phone me-1"></i>
                      Call Support
                    </a>
                    <a href="/help" className="btn btn-outline-secondary btn-sm">
                      <i className="fas fa-question-circle me-1"></i>
                      Help Center
                    </a>
                  </div>
                </div>
              )}
              
              <div className="mt-4">
                <small className="text-muted">
                  <i className="fas fa-clock me-1"></i>
                  Reported at {new Date().toLocaleTimeString()}
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfessionalErrorDisplay;