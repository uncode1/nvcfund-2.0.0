import React from 'react';
import ErrorMask from '../security/ErrorMask';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Classify error types without exposing technical details
    let errorType = 'general';
    
    if (error.message?.includes('Loading chunk') || 
        error.message?.includes('Loading CSS chunk') ||
        error.message?.includes('Cannot resolve module') ||
        error.message?.includes('ChunkLoadError') ||
        error.message?.includes('Loading failed for the script') ||
        error.name === 'ChunkLoadError') {
      errorType = 'loading';
    } else if (error.message?.includes('Network Error') ||
               error.message?.includes('fetch')) {
      errorType = 'network';
    }

    return { hasError: true, errorType };
  }

  componentDidCatch(error, errorInfo) {
    // Use ErrorMask system to handle errors professionally
    try {
      const errorMask = ErrorMask.getInstance ? ErrorMask.getInstance() : ErrorMask;
      if (errorMask && errorMask.handleMaskedError) {
        errorMask.handleMaskedError({
          type: 'react_boundary_error',
          message: 'Application error detected',
          component: this.constructor.name
        });
      }
    } catch (maskError) {
      // Fail silently if ErrorMask unavailable
    }
    
    this.setState({
      hasError: true,
      errorInfo: null, // Never store technical error info
      errorType: 'service_unavailable'
    });

    // Log internally without exposing details
    this.logErrorToService(error, errorInfo);
  }

  logErrorToService = (error, errorInfo) => {
    // Professional error reporting that never exposes technical details
    try {
      // Sanitized error data for monitoring (no technical exposure)
      const sanitizedError = {
        type: 'application_error',
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent.substring(0, 50), // Truncated for privacy
        url: window.location.pathname, // No query params for privacy
        incidentId: 'INC-' + Date.now().toString(36).toUpperCase()
      };
      
      // Internal logging only in development (never expose to user)
      if (process.env.NODE_ENV === 'development') {
        console.error('Internal Error Log:', sanitizedError);
      }
      
      // Store minimal info for support
      try {
        sessionStorage.setItem('last_error_incident', JSON.stringify(sanitizedError));
      } catch (storageError) {
        // Fail silently
      }
      
      // Send to backend monitoring (if available)
      fetch('/api/v1/security/events', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          type: 'frontend_error',
          details: sanitizedError,
          masked: true
        })
      }).catch(() => {
        // Fail silently - never expose monitoring failures
      });
    } catch (reportingError) {
      // Never expose reporting failures to users
    }
  };

  handleReload = () => {
    // Clear error state and reload the component
    this.setState({ hasError: false, errorInfo: null });
    window.location.reload();
  };

  handleGoHome = () => {
    // Navigate to home page
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="container-fluid py-5">
          <div className="row justify-content-center">
            <div className="col-md-8 col-lg-6">
              <div className="card shadow-sm border-0">
                <div className="card-body text-center py-5">
                  <div className="mb-4">
                    <i className="fas fa-shield-alt fa-4x text-primary"></i>
                  </div>
                  
                  <h3 className="mb-3 text-dark">Service Temporarily Unavailable</h3>
                  
                  <p className="text-muted mb-4 lead">
                    We're experiencing a brief service interruption. Your account and data remain secure.
                  </p>
                  
                  <div className="alert alert-light border mb-4">
                    <div className="d-flex align-items-center">
                      <i className="fas fa-info-circle text-info me-2"></i>
                      <small className="text-muted mb-0">
                        Our technical team has been automatically notified and is working to restore full service.
                      </small>
                    </div>
                  </div>
                  
                  <div className="d-flex flex-column flex-md-row gap-3 justify-content-center mb-4">
                    <button 
                      className="btn btn-primary px-4"
                      onClick={this.handleReload}
                    >
                      <i className="fas fa-redo me-2"></i>
                      Refresh Page
                    </button>
                    
                    <button 
                      className="btn btn-outline-primary px-4"
                      onClick={this.handleGoHome}
                    >
                      <i className="fas fa-home me-2"></i>
                      Return to Dashboard
                    </button>
                  </div>
                  
                  {/* Professional Help Section */}
                  <div className="mt-4 pt-4 border-top">
                    <h6 className="text-muted mb-3">Need Immediate Assistance?</h6>
                    <div className="row g-3">
                      <div className="col-md-4">
                        <a href="mailto:support@nvcbank.com" className="btn btn-outline-secondary btn-sm w-100">
                          <i className="fas fa-envelope me-1"></i>
                          Email Support
                        </a>
                      </div>
                      <div className="col-md-4">
                        <a href="tel:1-800-NVC-BANK" className="btn btn-outline-secondary btn-sm w-100">
                          <i className="fas fa-phone me-1"></i>
                          Call Support
                        </a>
                      </div>
                      <div className="col-md-4">
                        <a href="/help" className="btn btn-outline-secondary btn-sm w-100">
                          <i className="fas fa-question-circle me-1"></i>
                          Help Center
                        </a>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    <small className="text-muted">
                      <i className="fas fa-clock me-1"></i>
                      Service interruption reported at {new Date().toLocaleTimeString()}
                    </small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;