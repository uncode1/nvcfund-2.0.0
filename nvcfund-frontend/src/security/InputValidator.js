/**
 * Input Validation System
 * Harmonizes with backend validation and security standards
 */

export class InputValidator {
  constructor() {
    this.patterns = {
      email: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
      phone: /^\+?[\d\s\-\(\)]{10,15}$/,
      username: /^[a-zA-Z0-9._-]{3,30}$/,
      password: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
      accountNumber: /^[A-Z0-9]{8,20}$/,
      amount: /^\d+(\.\d{1,2})?$/,
      currency: /^[A-Z]{3}$/,
      routingNumber: /^\d{9}$/,
      ssn: /^\d{3}-?\d{2}-?\d{4}$/,
      zipCode: /^\d{5}(-\d{4})?$/
    };

    this.limits = {
      maxTransferAmount: 1000000,
      minTransferAmount: 0.01,
      maxDailyTransfers: 50,
      maxUsernameLength: 30,
      maxNameLength: 50,
      maxAddressLength: 200,
      maxDescriptionLength: 500
    };
  }

  // Main validation method
  validate(value, type, options = {}) {
    const result = {
      isValid: false,
      errors: [],
      sanitized: this.sanitize(value, type),
      value: null
    };

    try {
      // Basic null/undefined check
      if (this.isEmpty(value) && !options.optional) {
        result.errors.push(`${type} is required`);
        return result;
      }

      if (this.isEmpty(value) && options.optional) {
        result.isValid = true;
        return result;
      }

      // Type-specific validation
      switch (type) {
        case 'email':
          this.validateEmail(result);
          break;
        case 'password':
          this.validatePassword(result, options);
          break;
        case 'username':
          this.validateUsername(result);
          break;
        case 'amount':
          this.validateAmount(result, options);
          break;
        case 'phone':
          this.validatePhone(result);
          break;
        case 'accountNumber':
          this.validateAccountNumber(result);
          break;
        case 'name':
          this.validateName(result, options);
          break;
        case 'address':
          this.validateAddress(result);
          break;
        case 'description':
          this.validateDescription(result);
          break;
        case 'date':
          this.validateDate(result, options);
          break;
        default:
          this.validateGeneric(result, type, options);
      }

      // Apply additional constraints
      if (options.minLength && result.sanitized.length < options.minLength) {
        result.errors.push(`Minimum length is ${options.minLength} characters`);
      }

      if (options.maxLength && result.sanitized.length > options.maxLength) {
        result.errors.push(`Maximum length is ${options.maxLength} characters`);
      }

      result.isValid = result.errors.length === 0;
      if (result.isValid) {
        result.value = this.convert(result.sanitized, type);
      }

    } catch (error) {
      result.errors.push('Validation error occurred');
      console.error('Validation error:', error);
    }

    return result;
  }

  // Validation methods for specific types
  validateEmail(result) {
    if (!this.patterns.email.test(result.sanitized)) {
      result.errors.push('Please enter a valid email address');
    }
  }

  validatePassword(result, options) {
    const password = result.sanitized;
    
    if (password.length < 8) {
      result.errors.push('Password must be at least 8 characters long');
    }

    if (!this.patterns.password.test(password)) {
      result.errors.push('Password must contain uppercase, lowercase, number, and special character');
    }

    // Check for common weak passwords
    const weakPasswords = ['password', '123456', 'qwerty', 'abc123'];
    if (weakPasswords.includes(password.toLowerCase())) {
      result.errors.push('Password is too common. Please choose a stronger password');
    }

    // Check password confirmation if provided
    if (options.confirmPassword && password !== options.confirmPassword) {
      result.errors.push('Passwords do not match');
    }
  }

  validateUsername(result) {
    const username = result.sanitized;

    if (!this.patterns.username.test(username)) {
      result.errors.push('Username can only contain letters, numbers, dots, underscores, and hyphens');
    }

    if (username.length < 3) {
      result.errors.push('Username must be at least 3 characters long');
    }

    if (username.length > this.limits.maxUsernameLength) {
      result.errors.push(`Username cannot exceed ${this.limits.maxUsernameLength} characters`);
    }
  }

  validateAmount(result, options) {
    const amount = parseFloat(result.sanitized);

    if (isNaN(amount) || amount <= 0) {
      result.errors.push('Amount must be a positive number');
      return;
    }

    if (amount < this.limits.minTransferAmount) {
      result.errors.push(`Minimum amount is $${this.limits.minTransferAmount}`);
    }

    if (amount > this.limits.maxTransferAmount) {
      result.errors.push(`Maximum amount is $${this.limits.maxTransferAmount.toLocaleString()}`);
    }

    // Check decimal places
    const decimalPlaces = (result.sanitized.split('.')[1] || '').length;
    if (decimalPlaces > 2) {
      result.errors.push('Amount cannot have more than 2 decimal places');
    }

    // Custom limits
    if (options.max && amount > options.max) {
      result.errors.push(`Amount cannot exceed $${options.max.toLocaleString()}`);
    }

    if (options.min && amount < options.min) {
      result.errors.push(`Amount must be at least $${options.min}`);
    }
  }

  validatePhone(result) {
    if (!this.patterns.phone.test(result.sanitized)) {
      result.errors.push('Please enter a valid phone number');
    }
  }

  validateAccountNumber(result) {
    if (!this.patterns.accountNumber.test(result.sanitized)) {
      result.errors.push('Account number must be 8-20 alphanumeric characters');
    }
  }

  validateName(result, options) {
    const name = result.sanitized;

    if (name.length < 1) {
      result.errors.push('Name is required');
    }

    if (name.length > this.limits.maxNameLength) {
      result.errors.push(`Name cannot exceed ${this.limits.maxNameLength} characters`);
    }

    // Check for invalid characters
    if (!/^[a-zA-Z\s'-]+$/.test(name)) {
      result.errors.push('Name can only contain letters, spaces, hyphens, and apostrophes');
    }
  }

  validateAddress(result) {
    const address = result.sanitized;

    if (address.length > this.limits.maxAddressLength) {
      result.errors.push(`Address cannot exceed ${this.limits.maxAddressLength} characters`);
    }

    // Basic address validation
    if (!/^[a-zA-Z0-9\s,.-]+$/.test(address)) {
      result.errors.push('Address contains invalid characters');
    }
  }

  validateDescription(result) {
    const description = result.sanitized;

    if (description.length > this.limits.maxDescriptionLength) {
      result.errors.push(`Description cannot exceed ${this.limits.maxDescriptionLength} characters`);
    }
  }

  validateDate(result, options) {
    const date = new Date(result.sanitized);

    if (isNaN(date.getTime())) {
      result.errors.push('Please enter a valid date');
      return;
    }

    const now = new Date();

    if (options.futureOnly && date <= now) {
      result.errors.push('Date must be in the future');
    }

    if (options.pastOnly && date >= now) {
      result.errors.push('Date must be in the past');
    }

    if (options.minAge) {
      const minDate = new Date();
      minDate.setFullYear(minDate.getFullYear() - options.minAge);
      if (date > minDate) {
        result.errors.push(`Must be at least ${options.minAge} years old`);
      }
    }
  }

  validateGeneric(result, type, options) {
    // Generic validation for custom types
    if (options.pattern && !options.pattern.test(result.sanitized)) {
      result.errors.push(options.message || `Invalid ${type} format`);
    }
  }

  // Utility methods
  isEmpty(value) {
    return value === null || value === undefined || value === '';
  }

  sanitize(value, type) {
    if (this.isEmpty(value)) return '';

    let sanitized = String(value).trim();

    switch (type) {
      case 'email':
        sanitized = sanitized.toLowerCase();
        break;
      case 'username':
        sanitized = sanitized.toLowerCase();
        break;
      case 'amount':
        sanitized = sanitized.replace(/[^0-9.]/g, '');
        break;
      case 'phone':
        sanitized = sanitized.replace(/[^\d+\-\(\)\s]/g, '');
        break;
      case 'accountNumber':
        sanitized = sanitized.toUpperCase().replace(/[^A-Z0-9]/g, '');
        break;
      case 'name':
        sanitized = sanitized.replace(/[^a-zA-Z\s'-]/g, '');
        break;
      default:
        // Basic XSS prevention for text fields
        sanitized = sanitized
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;')
          .replace(/'/g, '&#x27;')
          .replace(/\//g, '&#x2F;');
    }

    return sanitized;
  }

  convert(value, type) {
    switch (type) {
      case 'amount':
        return parseFloat(value);
      case 'date':
        return new Date(value);
      default:
        return value;
    }
  }

  // Validation presets for common form combinations
  validateLoginForm(username, password) {
    return {
      username: this.validate(username, 'username'),
      password: this.validate(password, 'password')
    };
  }

  validateTransferForm(amount, fromAccount, toAccount, description) {
    return {
      amount: this.validate(amount, 'amount'),
      fromAccount: this.validate(fromAccount, 'accountNumber'),
      toAccount: this.validate(toAccount, 'accountNumber'),
      description: this.validate(description, 'description', { optional: true })
    };
  }

  validateRegistrationForm(userData) {
    return {
      username: this.validate(userData.username, 'username'),
      email: this.validate(userData.email, 'email'),
      password: this.validate(userData.password, 'password', { 
        confirmPassword: userData.confirmPassword 
      }),
      firstName: this.validate(userData.firstName, 'name'),
      lastName: this.validate(userData.lastName, 'name'),
      phone: this.validate(userData.phone, 'phone', { optional: true }),
      dateOfBirth: this.validate(userData.dateOfBirth, 'date', { 
        pastOnly: true, 
        minAge: 18 
      })
    };
  }

  // Check if all validations passed
  isFormValid(validationResults) {
    return Object.values(validationResults).every(result => result.isValid);
  }

  // Get all errors from validation results
  getFormErrors(validationResults) {
    const errors = [];
    Object.entries(validationResults).forEach(([field, result]) => {
      if (!result.isValid) {
        errors.push(`${field}: ${result.errors.join(', ')}`);
      }
    });
    return errors;
  }
}

// Create global validator instance
export const inputValidator = new InputValidator();

export default InputValidator;