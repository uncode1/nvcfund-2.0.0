"""
Flask Application Factory for Pure Modular Architecture
NVC Banking Platform - Enterprise-grade modular application factory
"""

import os
import logging
from flask import Flask, request, g, render_template
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# Import core extensions
from modules.core.extensions import (
    db, login_manager, csrf, socketio, 
    cache, rate_limiter, session_interface
)

# Import modular blueprint registration
from modules.core.modular_blueprint_registration import register_all_modular_blueprints

# Import enterprise logging system
from modules.core.enterprise_logging import get_enterprise_logger, EnterpriseLogger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize enterprise logging system
enterprise_logger = EnterpriseLogger()

# Initialize enterprise error logger
error_logger = get_enterprise_logger("errors")

def create_app(config_name=None):
    """
    Create and configure Flask application with modular architecture
    
    Args:
        config_name: Configuration environment (development, production, testing)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Configure application
    configure_app(app, config_name)
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Register modular blueprints
    register_all_modular_blueprints(app)
    
    # Register template context processors for role-based navigation
    from modules.core.template_context import register_template_context
    register_template_context(app)
    
    # Add basic root route with server-side authentication
    @app.route('/')
    def root():
        from flask_login import current_user
        from flask import render_template, redirect, url_for
        
        # Check if user is authenticated
        if current_user.is_authenticated:
            # User is logged in, serve the React app
            return render_template('main_app.html', user=current_user)
        else:
            # User is not logged in, redirect to login
            return redirect(url_for('auth.login'))
    
    # Test route for error logging
    @app.route('/test-error')
    def test_error():
        # Force a division by zero error to test logging
        result = 1 / 0
        return {'result': result}
    
    # Configure error handlers
    configure_error_handlers(app)
    
    # Configure middleware
    configure_middleware(app)
    
    logger.info("NVC Banking Platform initialized with Pure Modular Architecture")
    
    return app

def configure_app(app, config_name):
    """Configure Flask application settings"""
    
    # Import configuration classes
    from config import config
    
    # Load appropriate configuration
    config_obj = config.get(config_name or 'development')
    app.config.from_object(config_obj)
    
    # ProxyFix for Replit deployment
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

def initialize_extensions(app):
    """Initialize Flask extensions"""
    
    # Initialize enterprise logging system FIRST
    enterprise_logger.init_app(app)
    
    # Initialize database
    db.init_app(app)
    
    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Custom unauthorized handler for direct URL redirect
    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import redirect, request, session
        session['next_url'] = request.url
        return redirect('/auth/login')
    
    # Add user loader function
    @login_manager.user_loader
    def load_user(user_id):
        # Import here to avoid circular imports
        from modules.auth.models import User
        return User.query.get(user_id)
    
    # Initialize CSRF protection with enhanced settings
    csrf.init_app(app)
    
    # Configure additional CSRF settings
    app.config.setdefault('WTF_CSRF_TIME_LIMIT', 3600)
    app.config.setdefault('WTF_CSRF_SSL_STRICT', False)
    app.config.setdefault('WTF_CSRF_CHECK_DEFAULT', True)
    
    # Initialize SocketIO
    socketio.init_app(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
    
    # Initialize cache
    cache.init_app(app)
    
    # Initialize rate limiter
    rate_limiter.init_app(app)
    
    # Initialize session interface
    session_interface.init_app(app)
    
    # Initialize CORS
    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])
    
    # Create database tables and apply migrations
    with app.app_context():
        try:
            # Create new tables
            db.create_all()
            logger.info("Database tables created successfully")
            
            # Apply automatic migrations for existing tables
            from modules.core.database_migration import database_migration
            migration_success = database_migration.check_and_apply_migrations()
            
            if migration_success:
                logger.info("Database migrations applied successfully")
            else:
                logger.warning("Some database migrations failed - check logs")
                
        except Exception as e:
            logger.error(f"Database initialization error: {e}")

def configure_error_handlers(app):
    """Configure comprehensive error handlers with enterprise logging"""
    
    def is_api_request():
        """Check if this is an API request that should return JSON"""
        # API endpoints should return JSON
        if request.path.startswith('/api/'):
            return True
        
        # If the request explicitly asks for JSON
        if request.headers.get('Content-Type') == 'application/json':
            return True
            
        # Check Accept header for JSON preference (but not if HTML is preferred)
        accept_header = request.headers.get('Accept', '')
        # Only return JSON if specifically asking for JSON and NOT asking for HTML
        if accept_header and 'application/json' in accept_header and 'text/html' not in accept_header:
            return True
            
        # For anything else (including browsers), return HTML
        return False
    
    @app.errorhandler(404)
    def not_found(error):
        error_logger.warning(f"404 Not Found: {request.method} {request.path} from {request.remote_addr}")
        
        if is_api_request():
            return {'error': 'Resource not found'}, 404
        
        try:
            return render_template('errors/error_page.html', error_code=404), 404
        except:
            # Fallback to plain HTML if template fails
            return """
            <html><head><title>Page Not Found</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px; background: #0a2447; color: white;">
            <h1>404 - Page Not Found</h1>
            <p>The page you're looking for doesn't exist.</p>
            <a href="/" style="color: #66ccff;">Return to Homepage</a>
            </body></html>
            """, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        # Log to both standard logger and enterprise error logger
        logger.error(f"Internal server error: {error}")
        error_logger.error(f"500 Internal Server Error: {request.method} {request.path} from {request.remote_addr} - {str(error)}")
        
        if is_api_request():
            return {'error': 'Internal server error'}, 500
        
        try:
            return render_template('errors/error_page.html', error_code=500), 500
        except:
            # Fallback to plain HTML if template fails
            return """
            <html><head><title>Service Temporarily Unavailable</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px; background: #0a2447; color: white;">
            <h1>Service Temporarily Unavailable</h1>
            <p>We're experiencing technical difficulties. Our team has been notified.</p>
            <a href="/" style="color: #66ccff;">Return to Homepage</a>
            </body></html>
            """, 500
    
    @app.errorhandler(403)
    def forbidden(error):
        error_logger.warning(f"403 Forbidden: {request.method} {request.path} from {request.remote_addr}")
        
        if is_api_request():
            return {'error': 'Access forbidden'}, 403
            
        try:
            return render_template('errors/error_page.html', error_code=403), 403
        except:
            # Fallback to plain HTML if template fails
            return """
            <html><head><title>Access Forbidden</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px; background: #0a2447; color: white;">
            <h1>403 - Access Forbidden</h1>
            <p>You don't have permission to access this resource.</p>
            <a href="/auth/login" style="color: #66ccff;">Login</a>
            </body></html>
            """, 403
    
    @app.errorhandler(401)
    def unauthorized(error):
        error_logger.warning(f"401 Unauthorized: {request.method} {request.path} from {request.remote_addr}")
        
        if is_api_request():
            return {'error': 'Authentication required'}, 401
            
        try:
            return render_template('errors/error_page.html', error_code=401), 401
        except:
            # Fallback to plain HTML if template fails
            return """
            <html><head><title>Authentication Required</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px; background: #0a2447; color: white;">
            <h1>401 - Authentication Required</h1>
            <p>You need to log in to access this page.</p>
            <a href="/auth/login" style="color: #66ccff;">Login</a>
            </body></html>
            """, 401
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Catch all unhandled exceptions"""
        error_details = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'request_path': request.path,
            'request_method': request.method,
            'user_ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        }
        
        logger.error(f"Unhandled exception: {error}")
        error_logger.critical(f"Unhandled Exception: {type(error).__name__} - {str(error)} - Context: {error_details}")
        
        if is_api_request():
            return {'error': 'An unexpected error occurred'}, 500
        
        try:
            return render_template('errors/error_page.html', error_code=500), 500
        except:
            # Fallback to plain HTML if template fails
            return """
            <html><head><title>Unexpected Error</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px; background: #0a2447; color: white;">
            <h1>Unexpected Error</h1>
            <p>Something went wrong. Our technical team has been notified.</p>
            <a href="/" style="color: #66ccff;">Return to Homepage</a>
            </body></html>
            """, 500

def configure_middleware(app):
    """Configure middleware"""
    
    # Proxy fix for proper HTTPS handling
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Request logging middleware
    @app.before_request
    def log_request():
        logger.info(f"Request: {request.method} {request.path}")
    
    @app.after_request
    def log_response(response):
        logger.info(f"Response: {response.status_code}")
        return response

if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5000, debug=True)