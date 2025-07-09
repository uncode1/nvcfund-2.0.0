# NVC Banking Platform - Developer Guide

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Development Environment Setup](#development-environment-setup)
4. [Authentication & Security](#authentication--security)
5. [Modular Architecture](#modular-architecture)
6. [Database Schema](#database-schema)
7. [API Documentation](#api-documentation)
8. [Frontend Development](#frontend-development)
9. [Testing Guide](#testing-guide)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)

## Overview

The NVC Banking Platform is a comprehensive enterprise-grade banking application built with modern technologies and banking-grade security. It features a pure modular architecture with 34+ specialized financial service modules.

### Key Features
- **Sovereign Banking Operations**: Complete central banking capabilities
- **Treasury Management**: Advanced treasury operations and liquidity management
- **Cross-Clearing & Settlement**: Multi-currency settlement networks
- **Regulatory Compliance**: Built-in compliance frameworks
- **Blockchain Integration**: Full Ethereum/smart contract support
- **Real-time Analytics**: Advanced financial analytics and reporting
- **Multi-Role Authentication**: Banking-grade security with RBAC

### Technology Stack
- **Backend**: Flask 3.0+ with modular blueprint architecture
- **Frontend**: React 18.3+ with modern hooks and context API
- **Database**: PostgreSQL 15+ with SQLAlchemy ORM
- **Security**: Banking-grade data security with AES-256 encryption, JWT, CSRF protection
- **Data Protection**: Comprehensive data in transit and at rest encryption framework
- **Real-time**: SocketIO for WebSocket connections
- **Cache**: Redis for session storage and caching

## System Architecture

### Backend Architecture
```
nvcfund-backend/
├── app_factory.py          # Application factory pattern
├── main.py                 # WSGI entry point
├── config.py              # Configuration management
├── modules/               # Modular architecture
│   ├── auth/             # Authentication & user management
│   ├── banking/          # Core banking operations
│   ├── treasury/         # Treasury operations
│   ├── sovereign/        # Sovereign banking functions
│   ├── compliance/       # Regulatory compliance
│   ├── security_center/  # Comprehensive data security framework
│   │   ├── data_security.py              # Banking-grade encryption & transmission
│   │   ├── secure_models.py              # Automatic field-level encryption
│   │   ├── secure_routes.py              # Banking-grade route protection
│   │   └── data_security_implementation.py # Platform-wide security
│   ├── smart_contracts/  # Blockchain integration
│   └── [30+ other modules]
├── templates/            # Jinja2 templates
└── static/              # Static assets
```

### Frontend Architecture
```
nvcfund-frontend/
├── src/
│   ├── components/       # Reusable React components
│   ├── pages/           # Page components
│   ├── services/        # API service layer
│   ├── context/         # React context providers
│   └── utils/           # Utility functions
├── public/              # Public assets
└── build/               # Production build output
```

## Development Environment Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ with npm
- PostgreSQL 15+
- Redis 6+
- Git

### Backend Setup
1. **Clone and Setup Environment**
   ```bash
   git clone <repository>
   cd nvcfund-backend
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   ```bash
   # Copy and configure environment variables
   cp .env.example .env
   
   # Required variables:
   DATABASE_URL=postgresql://user:password@localhost/nvcbank
   SESSION_SECRET=your-secret-key-here
   FLASK_ENV=development
   ```

4. **Database Setup**
   ```bash
   # Create database
   createdb nvcbank
   
   # Run migrations
   python -c "from app_factory import create_app; from modules.core.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
   ```

5. **Run Development Server**
   ```bash
   python main.py
   # or
   gunicorn --bind 0.0.0.0:5000 --reload main:app
   ```

### Frontend Setup
1. **Navigate to Frontend**
   ```bash
   cd nvcfund-frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Environment Configuration**
   ```bash
   # Create .env file
   REACT_APP_API_URL=http://localhost:5000
   REACT_APP_ENVIRONMENT=development
   ```

4. **Run Development Server**
   ```bash
   npm start
   ```

## Authentication & Security

### Password Complexity Requirements
The platform enforces banking-grade password complexity:
- **Minimum 12 characters** length
- **At least 2 uppercase** letters
- **At least 2 lowercase** letters  
- **At least 2 numbers**
- **At least 2 special characters** (!@#$%^&*(),.?":{}|<>)
- **No common patterns** (password, admin, banking, etc.)
- **Maximum 2 repeated characters**
- **No consecutive sequences** (abc, 123, etc.)
- **Minimum 8 unique characters**

### Test Credentials
For development testing:
```
Username: uncode
Password: Zx9Wq2@#ComplexCeo
Role: super_admin

Username: regular_user  
Password: Ky5Rp8!$StandardUsr9
Role: USER

Username: demo_user
Password: Nz4Wq7@&SecureDmoTst
Role: USER
```

### Role-Based Access Control (RBAC)
- **super_admin**: Full system access
- **admin**: Administrative functions
- **treasury_officer**: Treasury operations
- **compliance_officer**: Compliance functions
- **USER**: Standard banking operations

## Comprehensive Data Security Framework

### Data Protection Architecture
The NVC Banking Platform implements banking-grade data security with comprehensive protection for both data in transit and data at rest across all application functions and modules.

### Core Security Components

#### 1. Data at Rest Protection
```python
# Automatic field-level encryption using secure mixins
from modules.security_center.secure_models import BankingAccountSecureMixin

class BankAccount(BankingAccountSecureMixin, db.Model):
    # Sensitive fields automatically encrypted
    def set_account_number(self, account_number):
        # Automatically encrypted with AES-256
        super().set_account_number(account_number)
    
    def get_masked_account_number(self):
        # Returns: ************1234
        return super().get_masked_account_number()
```

#### 2. Data in Transit Protection
```python
# Secure route decorators for banking-grade protection
from modules.security_center.secure_routes import banking_grade_security, secure_data_transmission

@banking_bp.route('/transfer', methods=['POST'])
@banking_grade_security(require_mfa=True, audit_level='detailed')
@secure_data_transmission(require_encryption=True)
def secure_transfer():
    # Request data automatically decrypted and validated
    # Response data automatically encrypted before transmission
    pass
```

#### 3. Encryption Standards
- **AES-256 encryption** for all sensitive data at rest
- **PBKDF2 with 100,000 iterations** for password hashing
- **HMAC-SHA256** for data integrity verification
- **End-to-end payload encryption** for data in transit
- **Cryptographically secure token generation**

#### 4. Secure Model Mixins
```python
# Available secure mixins for different data types
from modules.security_center.secure_models import (
    SecureFieldMixin,           # Base security functionality
    BankingAccountSecureMixin,  # Banking account data
    UserSecureMixin,           # User personal information
    TransactionSecureMixin     # Transaction data
)

class User(UserSecureMixin, db.Model):
    # Email, phone, address automatically encrypted
    def set_email(self, email):
        # Automatically encrypted
        super().set_email(email)
    
    def get_masked_email(self):
        # Returns: u***@example.com
        return super().get_masked_email()
```

#### 5. Security Validation
```python
# Comprehensive security testing and validation
from modules.security_center.data_security_implementation import (
    validate_platform_security,
    generate_security_report
)

# Validate all security measures
security_status = validate_platform_security()

# Generate compliance report
security_report = generate_security_report()
```

### Implementation Guidelines

#### Module Security Integration
```python
# Apply security to new modules
from modules.security_center.data_security_implementation import apply_module_security

# Automatically applies appropriate security measures
security_config = apply_module_security('your_module_name')
```

#### Environment Setup
```bash
# Required environment variable for production
export DATA_ENCRYPTION_KEY="base64-encoded-encryption-key"

# Generate secure encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Security Compliance
- **GDPR Compliance**: Personal data protection and encryption
- **PCI-DSS Compliance**: Credit card data encryption standards
- **SOX Compliance**: Financial data integrity and audit trails
- **Basel III Compliance**: Risk management data protection
- **Banking Regulations**: Multi-layer security enforcement

## Modular Architecture

### Module Structure
Each module follows this pattern:
```
modules/module_name/
├── __init__.py           # Module initialization
├── routes.py            # Flask routes/endpoints
├── services.py          # Business logic
├── models.py            # Database models
├── forms.py             # WTForms validation
├── config.py            # Module configuration
└── templates/           # Module templates
```

### Core Modules
1. **auth** - Authentication and user management
2. **banking** - Core banking operations (accounts, transactions)
3. **treasury** - Treasury management and liquidity
4. **sovereign** - Central banking operations
5. **compliance** - Regulatory compliance and reporting
6. **smart_contracts** - Blockchain and smart contract integration
7. **analytics** - Financial analytics and business intelligence
8. **cards_payments** - Card services and payment processing

### Creating New Modules
1. **Create Module Directory**
   ```bash
   mkdir -p modules/your_module/{templates,static}
   ```

2. **Module Blueprint Template**
   ```python
   # modules/your_module/routes.py
   from flask import Blueprint, render_template
   from modules.core.decorators import login_required
   
   your_module_bp = Blueprint('your_module', __name__, 
                             url_prefix='/your-module',
                             template_folder='templates')
   
   @your_module_bp.route('/')
   @login_required
   def index():
       return render_template('your_module/index.html')
   ```

3. **Register Module**
   ```python
   # modules/your_module/__init__.py
   from .routes import your_module_bp
   
   def init_app(app):
       app.register_blueprint(your_module_bp)
   ```

## Database Schema

### Core Tables
- **users** - User accounts and authentication
- **accounts** - Banking accounts (checking, savings, etc.)
- **transactions** - Financial transactions
- **security_events** - Security audit logs
- **communication_logs** - System communications
- **smart_contracts** - Blockchain contract registry

### Migration System
```bash
# Create migration
python -c "from modules.core.database_migration import create_migration; create_migration('description')"

# Apply migrations
python -c "from modules.core.database_migration import apply_migrations; apply_migrations()"
```

## API Documentation

### Authentication Endpoints
```http
POST /auth/login
POST /auth/logout
POST /auth/register
GET  /auth/profile
```

### Banking Operations
```http
GET  /banking/accounts
POST /banking/accounts
GET  /banking/transactions
POST /banking/transfer
```

### Treasury Operations
```http
GET  /treasury/liquidity
POST /treasury/reserves
GET  /treasury/settlements
```

### API Response Format
```json
{
  "success": true,
  "data": {},
  "message": "Operation successful",
  "timestamp": "2025-07-06T00:00:00Z"
}
```

## Frontend Development

### Component Structure
```jsx
// Professional banking component example
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { bankingAPI } from '../services/api';

const AccountSummary = () => {
  const { user } = useAuth();
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const response = await bankingAPI.getAccounts();
      setAccounts(response.data);
    } catch (error) {
      console.error('Failed to fetch accounts:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="account-summary">
      <h2>Account Summary</h2>
      {loading ? (
        <div className="spinner">Loading...</div>
      ) : (
        <div className="accounts-grid">
          {accounts.map(account => (
            <div key={account.id} className="account-card">
              <h3>{account.account_type}</h3>
              <p className="balance">${account.balance.toLocaleString()}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AccountSummary;
```

### State Management
```jsx
// AuthContext example
import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const login = async (username, password) => {
    try {
      const response = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData.user);
        setIsAuthenticated(true);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login }}>
      {children}
    </AuthContext.Provider>
  );
};
```

## Testing Guide

### Backend Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_authentication.py

# Run with coverage
python -m pytest --cov=modules tests/
```

### Frontend Testing
```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run specific test
npm test -- --testNamePattern="AccountSummary"
```

### Test Structure
```python
# tests/test_authentication.py
import pytest
from flask import url_for
from modules.auth.services import AuthService

def test_login_with_valid_credentials(client, app):
    """Test successful login with valid credentials"""
    response = client.post('/auth/login', data={
        'username': 'uncode',
        'password': 'Zx9Wq2@#ComplexCeo'
    })
    assert response.status_code == 302  # Redirect after successful login

def test_password_complexity_validation(app):
    """Test banking-grade password complexity"""
    with app.app_context():
        auth_service = AuthService()
        
        # Test weak password
        errors = auth_service.validate_password_complexity('weak123')
        assert len(errors) > 0
        
        # Test strong password
        errors = auth_service.validate_password_complexity('Zx9Wq2@#ComplexCeo')
        assert len(errors) == 0
```

## Deployment

### Production Configuration
```python
# config.py - Production settings
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)  # Banking compliance
    RATELIMIT_DEFAULT = '100 per hour'  # Per-user rate limiting
    CORS_ORIGINS = ['https://yourdomain.com']
```

### Security & Rate Limiting Features

#### Rate Limiting Configuration
- **Per-User Limits**: Individual rate limiting prevents account abuse
- **Environment-Specific**:
  - Development: 1000 requests/hour per user (convenient for testing)
  - Production: 100 requests/hour per user (banking security)
  - Testing: 10000 requests/hour per user (automated test support)
- **Banking Operations**: Enhanced limits for financial transactions (3 requests/minute)

#### Session Management
- **Production**: 15-minute timeout (banking compliance requirement)
- **Development**: 24-hour timeout (developer convenience)  
- **Testing**: 30-minute timeout (test scenario support)
- **Security**: HttpOnly, Secure, SameSite=Lax cookies in production

#### Advanced Security Features
- **IP-Based Protection**: Automatic blocking for abuse patterns
- **Progressive Penalties**: Escalating timeouts (15-minute blocks)
- **Multi-Layer Security**: Application, route, and IP-level protection
- **CSRF Protection**: 1-hour token lifetime

### Environment Variables
```bash
# Production environment variables
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SESSION_SECRET=your-production-secret
FLASK_ENV=production
REDIS_URL=redis://localhost:6379
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### WSGI Configuration
```python
# wsgi.py
from app_factory import create_app
import os

app = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == "__main__":
    app.run()
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database connection
   psql -h localhost -U username -d nvcbank
   
   # Verify environment variables
   echo $DATABASE_URL
   ```

2. **Module Import Errors**
   ```bash
   # Check Python path
   python -c "import sys; print(sys.path)"
   
   # Verify module structure
   ls -la modules/
   ```

3. **Authentication Issues**
   ```bash
   # Check session configuration
   python -c "from app_factory import create_app; app = create_app(); print(app.config['SESSION_SECRET'])"
   
   # Verify user credentials
   python -c "from modules.auth.services import AuthService; from app_factory import create_app; app = create_app(); app.app_context().push(); service = AuthService(); print(service.validate_password_complexity('your-password'))"
   ```

4. **Frontend API Connection**
   ```javascript
   // Check API configuration
   console.log(process.env.REACT_APP_API_URL);
   
   // Test API connection
   fetch('/api/health')
     .then(response => response.json())
     .then(data => console.log(data));
   ```

### Logging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Optimization
- Enable Redis caching for sessions
- Use connection pooling for database
- Implement CDN for static assets
- Enable gzip compression
- Use async operations where possible

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the coding standards
4. Write tests for new features
5. Submit a pull request

### Coding Standards
- Use PEP 8 for Python code
- Use ESLint for JavaScript/React
- Write comprehensive docstrings
- Follow the modular architecture pattern
- Maintain test coverage above 80%

---

For more information, contact the development team or refer to the API documentation.