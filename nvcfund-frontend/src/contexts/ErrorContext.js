import React, { createContext, useContext, useState, useCallback } from 'react';

/**
 * Central Error Handling Context
 * Provides application-wide error handling with professional user messaging
 */
const ErrorContext = createContext();

export const useGlobalError = () => {
  const context = useContext(ErrorContext);
  if (!context) {
    throw new Error('useGlobalError must be used within an ErrorProvider');
  }
  return context;
};

export const ErrorProvider = ({ children }) => {
  const [globalError, setGlobalError] = useState(null);
  const [isErrorVisible, setIsErrorVisible] = useState(false);

  // Professional error messages mapping
  const errorMessages = {
    // Network Errors
    'Network Error': 'Unable to connect to our services. Please check your internet connection.',
    'ERR_NETWORK': 'Connection failed. Please check your internet connection.',
    'ERR_INTERNET_DISCONNECTED': 'No internet connection detected.',
    
    // Authentication Errors
    'Invalid credentials': 'The username or password you entered is incorrect.',
    'Token expired': 'Your session has expired. Please sign in again.',
    'Unauthorized': 'You need to sign in to access this feature.',
    'Forbidden': 'You do not have permission to perform this action.',
    
    // Banking Errors
    'Insufficient funds': 'Insufficient account balance for this transaction.',
    'Account not found': 'The specified account could not be found.',
    'Transfer limit exceeded': 'This transfer exceeds your daily or monthly limit.',
    'Invalid account number': 'Please enter a valid account number.',
    'Transaction failed': 'Transaction could not be processed. Please try again.',
    
    // Validation Errors
    'Required field missing': 'Please fill in all required fields.',
    'Invalid email format': 'Please enter a valid email address.',
    'Password too weak': 'Password must meet security requirements.',
    'Invalid amount': 'Please enter a valid amount.',
    
    // Server Errors (all technical details hidden)
    'Internal Server Error': 'Our system is currently experiencing issues. Please try again later.',
    'Service Unavailable': 'Service is temporarily unavailable. Please try again in a few moments.',
    'Bad Gateway': 'Service connection issue. Please try again later.',
    'Gateway Timeout': 'Request timed out. Please try again.',
    
    // Rate Limiting
    'Too Many Requests': 'Too many attempts. Please wait a moment before trying again.',
    'Rate limit exceeded': 'You have made too many requests. Please wait before trying again.',
    
    // Default fallback
    'default': 'We are experiencing a brief service interruption. Please try again or contact support if the problem persists.'
  };

  // Filter out technical stack details completely
  const sanitizeError = useCallback((error) => {
    if (!error) return errorMessages.default;
    
    let message = '';
    if (typeof error === 'string') {
      message = error;
    } else if (error.message) {
      message = error.message;
    } else if (error.response?.data?.message) {
      message = error.response.data.message;
    } else if (error.response?.statusText) {
      message = error.response.statusText;
    } else {
      message = 'Unknown error';
    }

    const lowerMsg = message.toLowerCase();
    
    // Filter out any technical patterns
    const technicalPatterns = [
      'flask', 'python', 'sqlalchemy', 'psycopg2', 'traceback', 'exception',
      'postgresql', 'database', 'sql', 'column', 'table', 'query',
      'werkzeug', 'gunicorn', 'uwsgi', 'django', 'react', 'javascript',
      'node_modules', 'npm', 'yarn', 'webpack', 'babel', 'eslint',
      'import', 'module', 'function', 'class', 'method', 'attribute',
      'stack trace', 'line ', 'file ', 'error at', 'errno', 'enoent',
      'syntax error', 'reference error', 'type error', 'range error'
    ];
    
    // If message contains any technical patterns, return generic message
    if (technicalPatterns.some(pattern => lowerMsg.includes(pattern))) {
      return errorMessages.default;
    }
    
    // Map specific user-friendly errors
    for (const [key, value] of Object.entries(errorMessages)) {
      if (lowerMsg.includes(key.toLowerCase())) {
        return value;
      }
    }
    
    // Handle HTTP status codes
    if (error.response?.status) {
      const status = error.response.status;
      switch (status) {
        case 400:
          return 'Invalid request. Please check your input and try again.';
        case 401:
          return 'Your session has expired. Please sign in again.';
        case 403:
          return 'You do not have permission to perform this action.';
        case 404:
          return 'The requested information was not found.';
        case 429:
          return 'Too many requests. Please wait a moment before trying again.';
        case 500:
        case 502:
        case 503:
        case 504:
          return 'Our system is currently experiencing issues. Please try again later.';
        default:
          return errorMessages.default;
      }
    }
    
    return errorMessages.default;
  }, [errorMessages]);

  const showError = useCallback((error) => {
    const sanitizedMessage = sanitizeError(error);
    setGlobalError(sanitizedMessage);
    setIsErrorVisible(true);
    
    // Log technical details to console for debugging (hidden from user)
    console.error('Application Error (Technical Details):', error);
  }, [sanitizeError]);

  const hideError = useCallback(() => {
    setGlobalError(null);
    setIsErrorVisible(false);
  }, []);

  const clearError = useCallback(() => {
    hideError();
  }, [hideError]);

  const value = {
    globalError,
    isErrorVisible,
    showError,
    hideError,
    clearError,
    sanitizeError
  };

  return (
    <ErrorContext.Provider value={value}>
      {children}
    </ErrorContext.Provider>
  );
};

export default ErrorProvider;