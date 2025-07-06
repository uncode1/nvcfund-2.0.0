"""
Public Module Routes
NVC Banking Platform - Public-facing pages and contact functionality
"""

from flask import Blueprint, render_template, render_template_string, request, jsonify, redirect, url_for, flash
from datetime import datetime
from modules.utils.services import ErrorLoggerService
from typing import Dict, Any
import logging

# Import rate limiting from the correct location
try:
    from modules.core.decorators import rate_limit
except ImportError:
    # Fallback: create a simple rate limit decorator
    import functools
    def rate_limit(limit="60/minute"):
        def public_rate_limit_decorator(f):
            @functools.wraps(f)
            def decorated_function(*args, **kwargs):
                return f(*args, **kwargs)
            return decorated_function
        return public_rate_limit_decorator

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint with template folder - no URL prefix for public routes
public_bp = Blueprint('public', __name__, 
                     template_folder='templates')

# Import and register API blueprint
from .api import public_api_bp

# Initialize services
error_logger = ErrorLoggerService()

@public_bp.route('/')
def index():
    """Main landing page"""
    try:
        return render_template('public/index.html')
    except Exception as e:
        logger.error(f"Error rendering homepage: {e}")
        # Log the error but try to render the template with error handling
        error_logger.log_error(
            error_type="template_render_error",
            message=f"Failed to render homepage: {str(e)}",
            details={
                'route': 'public.index',
                'user_agent': request.headers.get('User-Agent', 'Unknown'),
                'ip_address': request.remote_addr
            }
        )
        # Return proper error page
        return render_template('public/500.html'), 500

@public_bp.route('/contact')
def contact():
    """Professional contact page"""
    try:
        return render_template('public/contact.html')
    except Exception as e:
        logger.error(f"Error rendering contact page: {e}")
        error_logger.log_error(
            error_type="template_render_error",
            message=f"Failed to render contact page: {str(e)}",
            details={
                'route': 'public.contact',
                'user_agent': request.headers.get('User-Agent', 'Unknown'),
                'ip_address': request.remote_addr
            }
        )
        # Fallback to a basic error message
        return """
        <div style="padding: 2rem; font-family: Arial;">
            <h1>Contact NVC Banking</h1>
            <p>We're experiencing technical difficulties. Please contact us directly:</p>
            <p><strong>Phone:</strong> +1 (800) 682-2265</p>
            <p><strong>Email:</strong> support@nvcfund.com</p>
        </div>
        """, 500

@public_bp.route('/contact/submit', methods=['POST'])
@rate_limit("3/minute")
def submit_contact():
    """Handle contact form submission"""
    try:
        # Get form data
        form_data = {
            'firstName': request.form.get('firstName', '').strip(),
            'lastName': request.form.get('lastName', '').strip(),
            'email': request.form.get('email', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'subject': request.form.get('subject', '').strip(),
            'message': request.form.get('message', '').strip()
        }

        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email', 'subject', 'message']
        missing_fields = [field for field in required_fields if not form_data.get(field)]

        if missing_fields:
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Email validation
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, form_data['email']):
            return jsonify({
                'status': 'error',
                'message': 'Please enter a valid email address'
            }), 400

        # Log contact submission
        logger.info(f"Contact form submission: {form_data['email']} - {form_data['subject']}")

        # Store contact inquiry (in a real system, this would save to database)
        contact_data = {
            **form_data,
            'timestamp': datetime.now().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        }

        # Log the contact inquiry
        error_logger.log_security_event(
            event_type="contact_form_submission",
            message=f"Contact form submitted by {contact_data.get('name', 'Unknown')}",
            user_id=None
        )

        return jsonify({
            'status': 'success',
            'message': 'Thank you for your message. We will respond within 2 hours.'
        })

    except Exception as e:
        logger.error(f"Error processing contact form: {e}")
        error_logger.log_error(
            error_type="contact_form_error",
            message=f"Failed to process contact form: {str(e)}",
            details={
                'route': 'public.submit_contact',
                'form_data': form_data if 'form_data' in locals() else {},
                'user_agent': request.headers.get('User-Agent', 'Unknown'),
                'ip_address': request.remote_addr
            }
        )
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while processing your request. Please try again.'
        }), 500


@public_bp.route('/api/contact', methods=['POST'])
# API endpoint without CSRF protection
@rate_limit("10/minute")  # 10 requests per minute for API contact submissions
def api_contact_submit():
    """API endpoint for contact form submission (CSRF-exempt for external use)"""
    logger = logging.getLogger(__name__)
    error_logger = ErrorLoggerService()

    try:
        # Check content type
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Content-Type must be application/json'
            }), 400

        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400

        # Extract form data from JSON
        form_data = {
            'firstName': data.get('firstName', '').strip(),
            'lastName': data.get('lastName', '').strip(),
            'email': data.get('email', '').strip(),
            'phone': data.get('phone', '').strip(),
            'subject': data.get('subject', '').strip(),
            'message': data.get('message', '').strip()
        }

        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email', 'subject', 'message']
        missing_fields = [field for field in required_fields if not form_data.get(field)]

        if missing_fields:
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Email validation
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, form_data['email']):
            return jsonify({
                'status': 'error',
                'message': 'Please enter a valid email address'
            }), 400

        # Additional validation for phone number if provided
        if form_data['phone']:
            phone_pattern = r'^[\+]?[\d\s\-\(\)]+$'
            if not re.match(phone_pattern, form_data['phone']):
                return jsonify({
                    'status': 'error',
                    'message': 'Please enter a valid phone number'
                }), 400

        # Log contact submission
        logger.info(f"API Contact form submission: {form_data['email']} - {form_data['subject']}")

        # Store contact inquiry (in a real system, this would save to database)
        contact_data = {
            **form_data,
            'timestamp': datetime.now().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'submission_method': 'api_json'
        }

        # Log the contact inquiry
        if error_logger:
            try:
                error_logger.log_security_event(
                    event_type="api_contact_form_submission",
                    message="API contact form submitted via JSON endpoint",
                    user_id=None
                )
            except Exception as log_error:
                logger.warning(f"Failed to log security event: {log_error}")

        return jsonify({
            'status': 'success',
            'message': 'Thank you for your message. We will respond within 2 hours.',
            'data': {
                'submission_id': f"contact_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'timestamp': contact_data['timestamp'],
                'email': form_data['email']
            }
        }), 200

    except Exception as e:
        logger.error(f"Error processing API contact form: {e}")
        if error_logger:
            try:
                error_logger.log_error(
                    error_type="api_contact_form_error",
                    message=f"Failed to process API contact form: {str(e)}",
                    details={
                        'route': 'public.api_contact_submit',
                        'data': data if 'data' in locals() else {},
                        'user_agent': request.headers.get('User-Agent', 'Unknown'),
                        'ip_address': request.remote_addr
                    }
                )
            except Exception as log_error:
                logger.warning(f"Failed to log error: {log_error}")

        return jsonify({
            'status': 'error',
            'message': 'An error occurred while processing your request. Please try again.'
        }), 500


@public_bp.route('/about')
def about():
    """About NVC Banking page"""
    try:
        return render_template('public/about.html')
    except Exception as e:
        logger.error(f"Error rendering about page: {e}")
        return "About page temporarily unavailable", 500

@public_bp.route('/services')
def services():
    """Banking services overview page"""
    try:
        return render_template('public/services.html')
    except Exception as e:
        logger.error(f"Error rendering services page: {e}")
        return "Page temporarily unavailable", 500

@public_bp.route('/privacy-policy')
def privacy_policy():
    """Privacy policy page"""
    try:
        return render_template('public/privacy_policy.html')
    except Exception as e:
        logger.error(f"Error rendering privacy policy page: {e}")
        return "Page temporarily unavailable", 500

@public_bp.route('/terms-of-service')
def terms_of_service():
    """Terms of service page"""
    try:
        return render_template('public/terms_of_service.html')
    except Exception as e:
        logger.error(f"Error rendering terms of service page: {e}")
        return "Page temporarily unavailable", 500

@public_bp.route('/nvct-whitepaper')
def nvct_whitepaper():
    """NVCT Stablecoin whitepaper"""
    try:
        return render_template('public/nvct_whitepaper.html')
    except Exception as e:
        logger.error(f"Error rendering NVCT whitepaper: {e}")
        return "Page temporarily unavailable", 500

@public_bp.route('/getting-started')
def getting_started():
    """Getting started guide"""
    try:
        return render_template('public/getting_started.html')
    except Exception as e:
        logger.error(f"Error rendering getting started page: {e}")
        return "Page temporarily unavailable", 500

@public_bp.route('/user-guide')
def user_guide():
    """User guide page"""
    try:
        return render_template('public/user_guide.html')
    except Exception as e:
        logger.error(f"Error rendering user guide page: {e}")
        return "Page temporarily unavailable", 500

@public_bp.route('/faq')
def faq():
    """Frequently asked questions"""
    try:
        return render_template('public/faq.html')
    except Exception as e:
        logger.error(f"Error rendering FAQ page: {e}")
        return "Page temporarily unavailable", 500

@public_bp.route('/documentation')
def documentation():
    """Documentation center"""
    try:
        return render_template('public/documentation.html')
    except Exception as e:
        logger.error(f"Error rendering documentation page: {e}")
        return "Page temporarily unavailable", 500

@public_bp.route('/api-documentation')
@public_bp.route('/api_documentation')
def api_documentation():
    """API documentation page"""
    try:
        return render_template('public/api_documentation.html')
    except Exception as e:
        logger.error(f"Error rendering API documentation page: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return "Page temporarily unavailable", 500

@public_bp.route('/whitepaper')
@public_bp.route('/nvct_whitepaper')
def whitepaper():
    """NVCT Whitepaper page"""
    try:
        return render_template('public/nvct_whitepaper.html')
    except Exception as e:
        logger.error(f"Error rendering whitepaper page: {e}")
        return "Page temporarily unavailable", 500

@public_bp.route('/download-whitepaper')
def download_whitepaper():
    """Download NVCT whitepaper"""
    try:
        flash('NVCT Whitepaper download will be available soon', 'info')
        return redirect(url_for('public.nvct_whitepaper'))
    except Exception as e:
        logger.error(f"Error handling whitepaper download: {e}")
        return redirect(url_for('public.nvct_whitepaper'))

@public_bp.route('/contact-support')
def contact_support():
    """Contact support page"""
    try:
        return render_template('public/contact_support.html')
    except Exception as e:
        logger.error(f"Error rendering contact support page: {e}")
        return "Page temporarily unavailable", 500

@public_bp.route('/public-documentation')
def public_documentation():
    """Public documentation page"""
    try:
        return render_template('public/public_documentation.html')
    except Exception as e:
        logger.error(f"Error rendering public documentation page: {e}")
        return "Page temporarily unavailable", 500

# Health check endpoint
@public_bp.route('/api/health')
def health_check():
    """Public module health check"""
    try:
        return jsonify({
            'status': 'healthy',
            'app_module': 'public',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# Error handlers
@public_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 error in public module: {request.url}")
    return render_template('404.html'), 404

@public_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error in public module: {str(error)}")
    return render_template('500.html'), 500

# Module registration information
MODULE_INFO = {
    'name': 'Public Module',
    'version': '1.0.0',
    'description': 'Public-facing pages and contact functionality',
    'routes': [
        '/public/contact',
        '/public/about',
        '/public/services',
        '/public/privacy-policy',
        '/public/terms-of-service',
        '/public/nvct-whitepaper',
        '/public/getting-started',
        '/public/user-guide',
        '/public/faq',
        '/public/documentation'
    ],
    'api_endpoints': [
        '/public/contact/submit',
        '/public/api/health'
    ],
    'features': [
        'Contact form processing',
        'Public information pages',
        'Documentation center',
        'Legal pages',
        'Health monitoring'
    ],
    'dependencies': [
        'utils.services.ErrorLoggerService',
        'core.decorators.rate_limit'
    ],
    'status': 'active'
}

def get_module_info():
    """Get module information"""
    return MODULE_INFO