"""
Configuration Classes for NVC Banking Platform
Supports development, testing, and production environments
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class with common settings"""
    
    # Security
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Session Management
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = 'flask_session'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'nvc_banking:'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)
    
    # Cache Configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Rate Limiting
    RATELIMIT_STORAGE_URI = 'memory://'
    RATELIMIT_DEFAULT = '1000 per hour'
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # CORS - Environment configurable
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
    
    # Proxy configuration
    BEHIND_PROXY = os.environ.get('BEHIND_PROXY', 'false').lower() == 'true'
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Plaid Configuration
    PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
    PLAID_SECRET = os.environ.get('PLAID_SECRET')
    PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox')
    
    # Binance Configuration
    BINANCE_CLIENT_ID = os.environ.get('BINANCE_CLIENT_ID')
    BINANCE_CLIENT_SECRET = os.environ.get('BINANCE_CLIENT_SECRET')


class DevelopmentConfig(Config):
    """Development configuration for sandbox environment"""
    
    DEBUG = True
    TESTING = False
    
    # Database - Use SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'sqlite:///nvc_banking_dev.db'
    )
    
    # Enhanced CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SSL_STRICT = False  # Allow non-SSL in development
    WTF_CSRF_CHECK_DEFAULT = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    
    # Database-specific settings for development
    DATABASE_URL_CHECK = os.environ.get('DATABASE_URL', 'sqlite:///nvc_banking_dev.db')
    if 'sqlite' in DATABASE_URL_CHECK:
        # SQLite settings
        SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {
                "check_same_thread": False,  # Allow SQLite multi-threading
                "timeout": 20,  # Connection timeout
            }
        }
    else:
        # PostgreSQL settings
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_recycle": 300,
            "pool_pre_ping": True,
        }
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    
    # Session timeout (extended for development)
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)


class TestingConfig(Config):
    """Testing configuration with optimized settings for automated tests"""
    
    TESTING = True
    DEBUG = False
    
    # Use in-memory SQLite database for fast, isolated tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for easier testing of POST requests
    WTF_CSRF_ENABLED = False
    
    # Use simple cache for testing
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 10  # Short timeout for testing
    
    # Use in-memory rate limit storage for testing
    RATELIMIT_STORAGE_URI = 'memory://'
    RATELIMIT_DEFAULT = '10000 per hour'  # High limit for testing
    
    # Disable email sending in tests
    MAIL_SUPPRESS_SEND = True
    
    # Session configuration for testing
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = 'test_sessions'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Logging
    LOG_LEVEL = 'WARNING'  # Reduce log noise during tests
    
    # Test-specific settings
    SERVER_NAME = 'localhost.localdomain'
    APPLICATION_ROOT = '/'
    PREFERRED_URL_SCHEME = 'http'
    
    # Security settings for testing
    SECRET_KEY = 'test-secret-key-for-testing-only'
    
    # API Configuration for testing
    PLAID_ENV = 'sandbox'
    
    # Disable external API calls during testing
    EXTERNAL_API_ENABLED = False


class ProductionConfig(Config):
    """Production configuration with security hardening"""
    
    DEBUG = False
    TESTING = False
    
    # Production database URI - will be validated at runtime
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://user:pass@localhost/nvc_banking_prod')
    
    # Enable proxy fix in production (typically behind nginx/apache)
    BEHIND_PROXY = True
    
    # Enhanced security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Shorter session timeout for production
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)
    
    # Rate limiting - more restrictive in production
    RATELIMIT_DEFAULT = '100 per hour'
    
    # Logging
    LOG_LEVEL = 'INFO'
    
    # CORS - more restrictive in production (should be set via environment)
    CORS_ORIGINS = []
    
    # SSL/TLS
    PREFERRED_URL_SCHEME = 'https'
    
    @classmethod
    def validate_production_requirements(cls):
        """Validate required environment variables for production"""
        required_vars = ['SECRET_KEY', 'DATABASE_URL']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            raise ValueError(
                f"Production requires the following environment variables: {', '.join(missing_vars)}"
            )
    
    # Database - Use PostgreSQL for production
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'postgresql://user:pass@localhost/nvc_banking_prod'
    )
    
    # Enhanced security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Shorter session timeout for production
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)
    
    # Rate limiting - more restrictive in production
    RATELIMIT_DEFAULT = '100 per hour'
    
    # Logging
    LOG_LEVEL = 'INFO'
    
    # CORS - more restrictive in production
    CORS_ORIGINS = []  # Set specific domains in production
    
    # SSL/TLS
    PREFERRED_URL_SCHEME = 'https'
    
    # Production API settings
    PLAID_ENV = 'production'
    EXTERNAL_API_ENABLED = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}