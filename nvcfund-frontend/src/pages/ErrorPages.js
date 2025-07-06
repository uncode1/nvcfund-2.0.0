import React from 'react';
import { useNavigate } from 'react-router-dom';

// Professional 404 Page
export const NotFoundPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-lg-6 col-md-8 text-center">
            <div className="card border-0 shadow-lg">
              <div className="card-body p-5">
                <div className="mb-4">
                  <i className="fas fa-exclamation-triangle fa-4x text-warning mb-3"></i>
                  <h1 className="display-4 text-primary mb-3">404</h1>
                  <h3 className="text-dark mb-3">Page Not Found</h3>
                  <p className="text-muted mb-4">
                    The page you're looking for doesn't exist or has been moved. 
                    This might happen when accessing an invalid URL or outdated link.
                  </p>
                </div>
                <div className="d-grid gap-2 d-md-flex justify-content-md-center">
                  <button 
                    className="btn btn-primary me-md-2"
                    onClick={() => navigate('/')}
                  >
                    <i className="fas fa-home me-2"></i>Return Home
                  </button>
                  <button 
                    className="btn btn-outline-secondary"
                    onClick={() => navigate(-1)}
                  >
                    <i className="fas fa-arrow-left me-2"></i>Go Back
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Professional 500 Page
export const ServerErrorPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-lg-6 col-md-8 text-center">
            <div className="card border-0 shadow-lg">
              <div className="card-body p-5">
                <div className="mb-4">
                  <i className="fas fa-server fa-4x text-danger mb-3"></i>
                  <h1 className="display-4 text-primary mb-3">500</h1>
                  <h3 className="text-dark mb-3">Service Temporarily Unavailable</h3>
                  <p className="text-muted mb-4">
                    We're experiencing technical difficulties. Our team has been notified 
                    and is working to resolve the issue. Please try again in a few minutes.
                  </p>
                </div>
                <div className="d-grid gap-2 d-md-flex justify-content-md-center">
                  <button 
                    className="btn btn-primary me-md-2"
                    onClick={() => navigate('/')}
                  >
                    <i className="fas fa-home me-2"></i>Return Home
                  </button>
                  <button 
                    className="btn btn-outline-secondary"
                    onClick={() => window.location.reload()}
                  >
                    <i className="fas fa-redo me-2"></i>Try Again
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Professional Access Denied Page (for treasury operations)
export const AccessDeniedPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-lg-6 col-md-8 text-center">
            <div className="card border-0 shadow-lg">
              <div className="card-body p-5">
                <div className="mb-4">
                  <i className="fas fa-shield-alt fa-4x text-warning mb-3"></i>
                  <h1 className="display-4 text-primary mb-3">403</h1>
                  <h3 className="text-dark mb-3">Access Restricted</h3>
                  <p className="text-muted mb-4">
                    This section requires special authorization. Treasury operations are 
                    restricted to authorized personnel only, following our security protocols.
                  </p>
                </div>
                <div className="d-grid gap-2 d-md-flex justify-content-md-center">
                  <button 
                    className="btn btn-primary me-md-2"
                    onClick={() => navigate('/dashboard')}
                  >
                    <i className="fas fa-chart-line me-2"></i>Go to Dashboard
                  </button>
                  <button 
                    className="btn btn-outline-secondary"
                    onClick={() => navigate(-1)}
                  >
                    <i className="fas fa-arrow-left me-2"></i>Go Back
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Professional Network Error Page
export const NetworkErrorPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-lg-6 col-md-8 text-center">
            <div className="card border-0 shadow-lg">
              <div className="card-body p-5">
                <div className="mb-4">
                  <i className="fas fa-wifi fa-4x text-info mb-3"></i>
                  <h1 className="display-4 text-primary mb-3">Connection Issue</h1>
                  <h3 className="text-dark mb-3">Network Unavailable</h3>
                  <p className="text-muted mb-4">
                    Unable to connect to our services. Please check your internet connection 
                    and try again. If the problem persists, contact support.
                  </p>
                </div>
                <div className="d-grid gap-2 d-md-flex justify-content-md-center">
                  <button 
                    className="btn btn-primary me-md-2"
                    onClick={() => window.location.reload()}
                  >
                    <i className="fas fa-redo me-2"></i>Retry Connection
                  </button>
                  <button 
                    className="btn btn-outline-secondary"
                    onClick={() => navigate('/')}
                  >
                    <i className="fas fa-home me-2"></i>Return Home
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Professional Loading Page for import errors
export const LoadingErrorPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-lg-6 col-md-8 text-center">
            <div className="card border-0 shadow-lg">
              <div className="card-body p-5">
                <div className="mb-4">
                  <i className="fas fa-hourglass-half fa-4x text-primary mb-3"></i>
                  <h3 className="text-dark mb-3">Service Loading</h3>
                  <p className="text-muted mb-4">
                    Our services are initializing. This usually takes just a moment. 
                    If this persists, please refresh the page or contact support.
                  </p>
                </div>
                <div className="d-grid gap-2 d-md-flex justify-content-md-center">
                  <button 
                    className="btn btn-primary me-md-2"
                    onClick={() => window.location.reload()}
                  >
                    <i className="fas fa-redo me-2"></i>Refresh Page
                  </button>
                  <button 
                    className="btn btn-outline-secondary"
                    onClick={() => navigate('/')}
                  >
                    <i className="fas fa-home me-2"></i>Return Home
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Professional Maintenance Page
export const MaintenancePage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-lg-6 col-md-8 text-center">
            <div className="card border-0 shadow-lg">
              <div className="card-body p-5">
                <div className="mb-4">
                  <i className="fas fa-tools fa-4x text-warning mb-3"></i>
                  <h3 className="text-dark mb-3">Scheduled Maintenance</h3>
                  <p className="text-muted mb-4">
                    We're performing scheduled maintenance to improve our services. 
                    Normal operations will resume shortly. Thank you for your patience.
                  </p>
                </div>
                <div className="d-grid gap-2 d-md-flex justify-content-md-center">
                  <button 
                    className="btn btn-primary me-md-2"
                    onClick={() => window.location.reload()}
                  >
                    <i className="fas fa-redo me-2"></i>Check Status
                  </button>
                  <button 
                    className="btn btn-outline-secondary"
                    onClick={() => navigate('/')}
                  >
                    <i className="fas fa-home me-2"></i>Return Home
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const ErrorPages = {
  NotFoundPage,
  ServerErrorPage,
  AccessDeniedPage,
  NetworkErrorPage,
  LoadingErrorPage,
  MaintenancePage
};

export default ErrorPages;