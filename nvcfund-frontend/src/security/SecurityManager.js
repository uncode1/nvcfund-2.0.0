/**
 * Frontend Security Manager
 * Harmonizes with backend's consolidated security engine
 * Provides enterprise-grade client-side security controls
 */

import CryptoJS from 'crypto-js';
import { getSecurityConfig, SecurityMessages, SecurityUtils } from './SecurityConfig';

export class SecurityManager {
  constructor() {
    this.config = getSecurityConfig();
    this.sessionTimeout = this.config.session.timeout;
    this.maxFailedAttempts = this.config.fraud.maxFailedLogins;
    this.sessionWarningTime = this.config.session.warningTime;
    this.csrfToken = null;
    this.encryptionKey = this.generateClientKey();
    
    this.initializeSecurity();
  }

  initializeSecurity() {
    // Initialize session monitoring
    this.startSessionMonitoring();
    
    // Initialize security headers validation
    this.validateSecurityHeaders();
    
    // Initialize input sanitization
    this.setupInputSanitization();
    
    // Initialize rate limiting tracking
    this.initRateLimitTracking();
  }

  // Session Security Management
  startSessionMonitoring() {
    // Monitor for inactivity
    let inactivityTimer;
    let warningTimer;
    let warningShown = false;

    const resetTimers = () => {
      clearTimeout(inactivityTimer);
      clearTimeout(warningTimer);
      warningShown = false;

      // Set warning timer
      warningTimer = setTimeout(() => {
        if (!warningShown) {
          this.showSessionWarning();
          warningShown = true;
        }
      }, this.sessionTimeout - this.sessionWarningTime);

      // Set logout timer
      inactivityTimer = setTimeout(() => {
        this.handleSessionTimeout();
      }, this.sessionTimeout);
    };

    // Track user activity
    const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    activityEvents.forEach(event => {
      document.addEventListener(event, resetTimers, true);
    });

    resetTimers();
  }

  showSessionWarning() {
    if (window.showNotification) {
      window.showNotification('warning', SecurityMessages.session.warning);
    }
  }

  handleSessionTimeout() {
    // Clear sensitive data
    this.clearSensitiveData();
    
    // Notify user
    if (window.showNotification) {
      window.showNotification('info', 'Session expired for security. Please log in again.');
    }
    
    // Redirect to login
    window.location.href = '/login';
  }

  // Input Validation and Sanitization
  setupInputSanitization() {
    // Create global input sanitizer
    window.sanitizeInput = this.sanitizeInput.bind(this);
    window.validateAmount = this.validateAmount.bind(this);
    window.validateAccountNumber = this.validateAccountNumber.bind(this);
  }

  sanitizeInput(input, type = 'text') {
    if (!input) return '';
    
    let sanitized = String(input).trim();
    
    switch (type) {
      case 'username':
        // Allow alphanumeric and common username characters
        sanitized = sanitized.replace(/[^a-zA-Z0-9._-]/g, '');
        break;
      case 'amount':
        // Allow only numbers and decimal point
        sanitized = sanitized.replace(/[^0-9.]/g, '');
        break;
      case 'accountNumber':
        // Allow only alphanumeric characters
        sanitized = sanitized.replace(/[^a-zA-Z0-9]/g, '');
        break;
      case 'text':
      default:
        // Basic XSS prevention
        sanitized = sanitized
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;')
          .replace(/'/g, '&#x27;')
          .replace(/\//g, '&#x2F;');
        break;
    }
    
    return sanitized;
  }

  validateAmount(amount) {
    const sanitized = this.sanitizeInput(amount, 'amount');
    const num = parseFloat(sanitized);
    
    return {
      isValid: !isNaN(num) && num > 0 && num <= 1000000,
      value: num,
      sanitized
    };
  }

  validateAccountNumber(accountNumber) {
    const sanitized = this.sanitizeInput(accountNumber, 'accountNumber');
    
    return {
      isValid: /^[A-Z0-9]{8,20}$/.test(sanitized),
      sanitized
    };
  }

  // Rate Limiting Client-Side Tracking
  initRateLimitTracking() {
    this.rateLimits = new Map();
  }

  checkRateLimit(action, maxAttempts = 5, windowMs = 60000) {
    const now = Date.now();
    const key = action;
    
    if (!this.rateLimits.has(key)) {
      this.rateLimits.set(key, []);
    }
    
    const attempts = this.rateLimits.get(key);
    
    // Remove old attempts outside the window
    const recentAttempts = attempts.filter(time => now - time < windowMs);
    this.rateLimits.set(key, recentAttempts);
    
    if (recentAttempts.length >= maxAttempts) {
      return {
        allowed: false,
        retryAfter: Math.ceil((recentAttempts[0] + windowMs - now) / 1000)
      };
    }
    
    recentAttempts.push(now);
    this.rateLimits.set(key, recentAttempts);
    
    return { allowed: true };
  }

  // Data Encryption/Decryption for Sensitive Client Storage
  generateClientKey() {
    // Generate a client-side encryption key (not for server communication)
    return CryptoJS.lib.WordArray.random(256/8).toString();
  }

  encryptSensitiveData(data) {
    try {
      return CryptoJS.AES.encrypt(JSON.stringify(data), this.encryptionKey).toString();
    } catch (error) {
      console.error('Encryption failed:', error);
      return null;
    }
  }

  decryptSensitiveData(encryptedData) {
    try {
      const bytes = CryptoJS.AES.decrypt(encryptedData, this.encryptionKey);
      return JSON.parse(bytes.toString(CryptoJS.enc.Utf8));
    } catch (error) {
      console.error('Decryption failed:', error);
      return null;
    }
  }

  // Security Headers Validation
  validateSecurityHeaders() {
    // Check if security headers are present
    const checkHeaders = async () => {
      try {
        const response = await fetch('/api/v1/health', { method: 'HEAD' });
        const headers = response.headers;
        
        const securityHeaders = [
          'x-content-type-options',
          'x-frame-options',
          'x-xss-protection',
          'strict-transport-security'
        ];
        
        const missingHeaders = securityHeaders.filter(header => !headers.get(header));
        
        if (missingHeaders.length > 0) {
          console.warn('Missing security headers:', missingHeaders);
        }
      } catch (error) {
        console.error('Security header check failed:', error);
      }
    };
    
    checkHeaders();
  }

  // Failed Login Attempt Tracking
  trackFailedLogin(username) {
    const key = `failed_login_${username}`;
    const attempts = JSON.parse(localStorage.getItem(key) || '[]');
    const now = Date.now();
    
    // Add current attempt
    attempts.push(now);
    
    // Keep only recent attempts (last hour)
    const recentAttempts = attempts.filter(time => now - time < 3600000);
    
    localStorage.setItem(key, JSON.stringify(recentAttempts));
    
    if (recentAttempts.length >= this.maxFailedAttempts) {
      this.handleSuspiciousActivity('multiple_failed_logins', { username, attempts: recentAttempts.length });
      return false;
    }
    
    return true;
  }

  clearFailedLoginAttempts(username) {
    localStorage.removeItem(`failed_login_${username}`);
  }

  // Suspicious Activity Detection
  handleSuspiciousActivity(type, details) {
    console.warn('Suspicious activity detected:', type, details);
    
    // Log to backend
    this.reportSuspiciousActivity(type, details);
    
    // Show warning to user
    if (window.showNotification) {
      window.showNotification('warning', 'Suspicious activity detected. Please contact support if this continues.');
    }
  }

  async reportSuspiciousActivity(type, details) {
    try {
      await fetch('/api/v1/security/report-suspicious-activity', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          type,
          details,
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent,
          url: window.location.href
        })
      });
    } catch (error) {
      console.error('Failed to report suspicious activity:', error);
    }
  }

  // Clean up sensitive data
  clearSensitiveData() {
    // Clear tokens
    localStorage.removeItem('token');
    sessionStorage.clear();
    
    // Clear any cached sensitive data
    if ('caches' in window) {
      caches.keys().then(names => {
        names.forEach(name => caches.delete(name));
      });
    }
  }

  // Device Fingerprinting for Enhanced Security
  generateDeviceFingerprint() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillText('Device fingerprint', 2, 2);
    
    return {
      screen: `${window.screen.width}x${window.screen.height}`,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      language: navigator.language,
      platform: navigator.platform,
      userAgent: navigator.userAgent,
      canvas: canvas.toDataURL(),
      timestamp: Date.now()
    };
  }

  // Browser Security Check
  checkBrowserSecurity() {
    const issues = [];
    
    // Check if HTTPS
    if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost') {
      issues.push('Connection is not secure (HTTPS required)');
    }
    
    // Check for developer tools
    let devtools = false;
    const threshold = 160;
    
    if (window.outerHeight - window.innerHeight > threshold || 
        window.outerWidth - window.innerWidth > threshold) {
      devtools = true;
    }
    
    if (devtools) {
      this.handleSuspiciousActivity('developer_tools_detected', {});
    }
    
    return {
      secure: issues.length === 0,
      issues,
      devtools
    };
  }
}

// Create global security manager instance
export const securityManager = new SecurityManager();

// Export for use in other components
export default SecurityManager;