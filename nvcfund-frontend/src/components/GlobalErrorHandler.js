import React from 'react';
import { useGlobalError } from '../contexts/ErrorContext';

/**
 * Custom hook for handling errors in components
 * Provides a consistent way to display user-friendly error messages
 */
export const useErrorHandler = () => {
  const { showError } = useGlobalError();

  const handleError = (error, fallbackMessage = 'Service temporarily unavailable') => {
    let displayMessage = fallbackMessage;
    
    // Check if error has a user-friendly message
    if (error?.response?.data?.error) {
      displayMessage = error.response.data.error;
    } else if (error?.message && !error.message.includes('Network Error')) {
      displayMessage = error.message;
    }
    
    // Show the sanitized error message
    showError(displayMessage);
  };

  return { handleError };
};

/**
 * Global Error Handler Component
 * Displays centralized error notifications when errors occur
 */
const GlobalErrorHandler = () => {
  const { globalError, isErrorVisible, hideError } = useGlobalError();

  if (!isErrorVisible || !globalError) {
    return null;
  }

  return (
    <div 
      className="position-fixed w-100 h-100 d-flex align-items-center justify-content-center"
      style={{ 
        top: 0, 
        left: 0, 
        backgroundColor: 'rgba(0, 0, 0, 0.5)', 
        zIndex: 9999 
      }}
    >
      <div className="col-md-8 col-lg-6">
        <div className="card shadow-lg border-0">
          <div className="card-body text-center py-4">
            <div className="mb-3">
              <i className="fas fa-shield-alt fa-3x text-warning"></i>
            </div>
            
            <h5 className="mb-3 text-dark">Service Temporarily Unavailable</h5>
            
            <p className="text-muted mb-4">
              {globalError}
            </p>
            
            <div className="alert alert-light border mb-4">
              <div className="d-flex align-items-center justify-content-center">
                <i className="fas fa-info-circle text-info me-2"></i>
                <small className="text-muted mb-0">
                  Our technical team has been automatically notified.
                </small>
              </div>
            </div>
            
            <div className="d-flex flex-column flex-md-row gap-2 justify-content-center mb-3">
              <button 
                className="btn btn-primary px-4"
                onClick={() => {
                  hideError();
                  window.location.reload();
                }}
              >
                <i className="fas fa-redo me-2"></i>
                Try Again
              </button>
              
              <button 
                className="btn btn-outline-secondary px-4"
                onClick={() => {
                  hideError();
                  window.location.href = '/dashboard';
                }}
              >
                <i className="fas fa-home me-2"></i>
                Return to Dashboard
              </button>
              
              <button 
                className="btn btn-outline-secondary px-4"
                onClick={hideError}
              >
                <i className="fas fa-times me-2"></i>
                Close
              </button>
            </div>
            
            <div className="mt-3 pt-3 border-top">
              <h6 className="text-muted mb-2">Need Assistance?</h6>
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
            
            <div className="mt-3">
              <small className="text-muted">
                <i className="fas fa-clock me-1"></i>
                Reported at {new Date().toLocaleTimeString()}
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GlobalErrorHandler;