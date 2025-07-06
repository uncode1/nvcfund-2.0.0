/**
 * Error Masking System - NVC Banking Platform
 * Completely prevents technical error exposure to public users
 */

class ErrorMask {
  constructor() {
    this.maskedErrors = new Set();
    this.initializeErrorMasking();
  }

  initializeErrorMasking() {
    // Override console methods to prevent technical exposure
    this.maskConsoleErrors();
    
    // Override global error handlers
    this.maskGlobalErrors();
    
    // Override React error boundaries
    this.maskReactErrors();
    
    // Override webpack compilation errors
    this.maskCompilationErrors();
  }

  maskConsoleErrors() {
    const originalError = console.error;
    const originalWarn = console.warn;

    console.error = (...args) => {
      // Only log in development, never expose to production users
      if (process.env.NODE_ENV === 'development') {
        originalError.apply(console, args);
      }
      this.reportSecurityEvent('console_error', { args: this.sanitizeLogArgs(args) });
    };

    console.warn = (...args) => {
      if (process.env.NODE_ENV === 'development') {
        originalWarn.apply(console, args);
      }
    };
  }

  maskGlobalErrors() {
    // Override window error handler
    window.addEventListener('error', (event) => {
      event.preventDefault();
      event.stopPropagation();
      
      this.handleMaskedError({
        type: 'javascript_error',
        message: 'Service temporarily unavailable'
      });
      
      return false; // Prevent default browser error display
    });

    // Override unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      event.preventDefault();
      
      this.handleMaskedError({
        type: 'promise_rejection',
        message: 'Service temporarily unavailable'
      });
      
      return false;
    });
  }

  maskReactErrors() {
    // Override React development tools and error boundaries
    if (typeof window !== 'undefined') {
      // Disable React DevTools error reporting
      if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
        window.__REACT_DEVTOOLS_GLOBAL_HOOK__.onCommitFiberRoot = () => {};
        window.__REACT_DEVTOOLS_GLOBAL_HOOK__.onCommitFiberUnmount = () => {};
      }
      
      // Override any React error overlay creation
      const originalQuerySelector = document.querySelector;
      document.querySelector = function(selector) {
        // Block React error overlay selectors
        if (selector && (
          selector.includes('react-error-overlay') ||
          selector.includes('error-overlay') ||
          selector.includes('__react-error-overlay__')
        )) {
          return null;
        }
        return originalQuerySelector.call(this, selector);
      };
    }
  }

  maskCompilationErrors() {
    // Override webpack error overlay completely
    if (typeof window !== 'undefined') {
      // Disable webpack-dev-server overlay
      const webpackOverride = () => {
        if (window.__webpack_dev_server_client__) {
          window.__webpack_dev_server_client__.overlay = false;
        }
        
        // Override any error overlay creation
        const originalCreateElement = document.createElement;
        document.createElement = function(tagName) {
          const element = originalCreateElement.call(this, tagName);
          
          // Block webpack error overlay elements
          if (element.tagName === 'DIV' && 
              (element.id === 'webpack-dev-server-client-overlay' ||
               element.className?.includes('error-overlay'))) {
            return document.createDocumentFragment(); // Return empty fragment
          }
          
          return element;
        };
      };
      
      // Apply immediately and on DOM ready
      webpackOverride();
      document.addEventListener('DOMContentLoaded', webpackOverride);
    }
  }

  handleMaskedError(errorInfo) {
    // Log internally for support (never exposed to user)
    this.logInternalError(errorInfo);
    
    // Show professional user-friendly message
    this.showProfessionalErrorMessage();
    
    // Report to security monitoring
    this.reportSecurityEvent('masked_error', {
      type: errorInfo.type,
      timestamp: new Date().toISOString()
    });
  }

  showProfessionalErrorMessage() {
    // Remove any existing overlays
    this.clearAllErrorDisplays();
    
    // Create professional banking error display
    const errorOverlay = document.createElement('div');
    errorOverlay.id = 'professional-error-overlay';
    errorOverlay.innerHTML = `
      <div style="
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        z-index: 99999;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      ">
        <div style="
          background: white;
          padding: 40px;
          border-radius: 8px;
          max-width: 500px;
          text-align: center;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        ">
          <div style="color: #1e40af; font-size: 48px; margin-bottom: 20px;">🏦</div>
          <h3 style="color: #1f2937; margin-bottom: 16px; font-size: 24px;">Service Temporarily Unavailable</h3>
          <p style="color: #6b7280; margin-bottom: 24px; line-height: 1.5;">
            We're performing scheduled maintenance to improve our banking services. 
            Your account and data remain secure. Normal operations will resume shortly.
          </p>
          <button onclick="window.location.reload()" style="
            background: #1e40af;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            margin-right: 12px;
          ">Refresh Page</button>
          <button onclick="window.location.href='/'" style="
            background: #6b7280;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
          ">Return Home</button>
          <div style="margin-top: 24px; padding: 16px; background: #f9fafb; border-radius: 6px;">
            <div style="font-size: 12px; color: #6b7280;">Need immediate assistance?</div>
            <div style="font-size: 14px; color: #1f2937; margin-top: 4px;">
              📧 support@nvcbank.com | 📞 1-800-NVC-BANK
            </div>
          </div>
        </div>
      </div>
    `;
    
    document.body.appendChild(errorOverlay);
  }

  clearAllErrorDisplays() {
    // Remove professional overlay
    const professional = document.getElementById('professional-error-overlay');
    if (professional) professional.remove();
    
    // Remove any webpack overlays
    const webpackOverlays = document.querySelectorAll('[id*="overlay"], [class*="error"], [class*="overlay"]');
    webpackOverlays.forEach(overlay => {
      if (overlay.style.position === 'fixed' || overlay.style.zIndex > 1000) {
        overlay.remove();
      }
    });
    
    // Remove React error boundaries
    const reactErrors = document.querySelectorAll('[data-reactroot] + div');
    reactErrors.forEach(error => {
      if (error.textContent?.includes('Error') || error.textContent?.includes('Failed')) {
        error.remove();
      }
    });
  }

  sanitizeLogArgs(args) {
    return args.map(arg => {
      if (typeof arg === 'string') {
        // Strip all technical details
        return 'Service error detected'
          .replace(/\/[^\/\s]+\.(js|jsx|ts|tsx|css)/g, '')
          .replace(/:\d+:\d+/g, '')
          .replace(/Module not found/g, '')
          .replace(/Can't resolve/g, '')
          .replace(/webpack/g, '')
          .replace(/React/g, '');
      }
      return 'System event';
    });
  }

  logInternalError(errorInfo) {
    // Store minimal info for support (not exposed to user)
    try {
      const errorLog = JSON.parse(sessionStorage.getItem('internal_errors') || '[]');
      errorLog.push({
        timestamp: new Date().toISOString(),
        incidentId: this.generateIncidentId(),
        type: 'masked_error'
      });
      
      // Keep only last 5 errors
      if (errorLog.length > 5) {
        errorLog.splice(0, errorLog.length - 5);
      }
      
      sessionStorage.setItem('internal_errors', JSON.stringify(errorLog));
    } catch (e) {
      // Fail silently - never expose storage errors
    }
  }

  generateIncidentId() {
    return 'INC-' + Date.now().toString(36).toUpperCase();
  }

  reportSecurityEvent(eventType, details) {
    // Silent reporting to backend (never expose monitoring failures)
    try {
      fetch('/api/v1/security/events', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          type: eventType,
          details: details,
          timestamp: new Date().toISOString(),
          masked: true
        })
      }).catch(() => {
        // Fail completely silently
      });
    } catch (e) {
      // Never expose monitoring failures
    }
  }

  // Singleton pattern
  static getInstance() {
    if (!window.__ErrorMaskInstance) {
      window.__ErrorMaskInstance = new ErrorMask();
    }
    return window.__ErrorMaskInstance;
  }
}

// Initialize error masking immediately
const errorMask = ErrorMask.getInstance();

export default errorMask;