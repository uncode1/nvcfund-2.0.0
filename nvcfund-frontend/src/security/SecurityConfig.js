/**
 * Security Configuration
 * Centralized security settings that harmonize with backend security standards
 */

export const SecurityConfig = {
  // Session Management
  session: {
    timeout: 30 * 60 * 1000, // 30 minutes
    warningTime: 5 * 60 * 1000, // 5 minutes before timeout
    refreshThreshold: 5 * 60 * 1000, // Refresh token 5 minutes before expiry
  },

  // Rate Limiting
  rateLimits: {
    login: {
      attempts: 5,
      window: 300000, // 5 minutes
    },
    api: {
      attempts: 100,
      window: 60000, // 1 minute
    },
    transfer: {
      attempts: 10,
      window: 300000, // 5 minutes
    },
    password_reset: {
      attempts: 3,
      window: 900000, // 15 minutes
    },
  },

  // Input Validation
  validation: {
    password: {
      minLength: 8,
      requireUppercase: true,
      requireLowercase: true,
      requireNumbers: true,
      requireSpecialChars: true,
      maxLength: 128,
    },
    username: {
      minLength: 3,
      maxLength: 30,
      allowedChars: /^[a-zA-Z0-9._-]+$/,
    },
    amounts: {
      minTransferAmount: 0.01,
      maxTransferAmount: 1000000,
      maxDailyTransfers: 50,
      maxDecimalPlaces: 2,
    },
    account: {
      accountNumberPattern: /^[A-Z0-9]{8,20}$/,
      routingNumberPattern: /^\d{9}$/,
    },
  },

  // Security Headers (for validation)
  requiredHeaders: [
    'x-content-type-options',
    'x-frame-options', 
    'x-xss-protection',
    'strict-transport-security',
  ],

  // Encryption Settings
  encryption: {
    algorithm: 'AES',
    keySize: 256,
    ivSize: 16,
  },

  // Fraud Detection
  fraud: {
    maxFailedLogins: 3,
    suspiciousActivityThreshold: 5,
    deviceChangeThreshold: 3,
    locationChangeThreshold: 2,
  },

  // Monitoring
  monitoring: {
    logLevel: 'INFO',
    enableDeviceFingerprinting: true,
    enableBehaviorTracking: true,
    enableSecurityEventLogging: true,
  },

  // API Endpoints
  endpoints: {
    security: '/api/v1/security',
    auth: '/api/v1/auth',
    reporting: '/api/v1/security/report-suspicious-activity',
    health: '/api/v1/health',
  },

  // Environment-specific settings
  development: {
    enableDetailedLogging: true,
    skipCertificateValidation: false,
    enableDebugMode: false,
  },

  production: {
    enableDetailedLogging: false,
    enforceHTTPS: true,
    enableCSP: true,
  },
};

// Get environment-specific configuration
export const getSecurityConfig = () => {
  const env = process.env.NODE_ENV || 'development';
  return {
    ...SecurityConfig,
    ...(SecurityConfig[env] || {}),
  };
};

// Security validation patterns
export const ValidationPatterns = {
  email: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  phone: /^\+?[\d\s\-\(\)]{10,15}$/,
  ssn: /^\d{3}-?\d{2}-?\d{4}$/,
  zipCode: /^\d{5}(-\d{4})?$/,
  creditCard: /^\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}$/,
  url: /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/,
};

// Security error messages
export const SecurityMessages = {
  session: {
    timeout: 'Your session has expired for security. Please log in again.',
    warning: 'Your session will expire in 5 minutes. Please save your work.',
  },
  rateLimit: {
    exceeded: 'Too many attempts. Please try again later.',
    blocked: 'Account temporarily blocked due to security concerns.',
  },
  validation: {
    required: 'This field is required',
    invalid: 'Please enter a valid value',
    tooShort: 'Value is too short',
    tooLong: 'Value is too long',
    weakPassword: 'Password does not meet security requirements',
  },
  security: {
    suspiciousActivity: 'Suspicious activity detected. Please contact support if this continues.',
    deviceChange: 'Login from new device detected. Please verify your identity.',
    locationChange: 'Login from new location detected. Security verification required.',
  },
};

// Security utility functions
export const SecurityUtils = {
  // Generate secure random string
  generateSecureRandom: (length = 32) => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  },

  // Check if running in secure context
  isSecureContext: () => {
    return window.isSecureContext || window.location.protocol === 'https:' || window.location.hostname === 'localhost';
  },

  // Get current timestamp
  getTimestamp: () => new Date().toISOString(),

  // Format security event
  formatSecurityEvent: (type, details) => ({
    type,
    details,
    timestamp: SecurityUtils.getTimestamp(),
    userAgent: navigator.userAgent,
    url: window.location.href,
  }),
};

export default SecurityConfig;