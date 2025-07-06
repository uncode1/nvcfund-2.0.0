"""
Public Module API
NVC Banking Platform - RESTful API endpoints for public module
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Dict, Any, List
import logging
import re

# Configure logging
logger = logging.getLogger(__name__)

# Create API blueprint
public_api_bp = Blueprint('public_api', __name__, url_prefix='/api/v1/public')

# Import services
try:
    from modules.utils.services import ErrorLoggerService
    error_logger = ErrorLoggerService()
except ImportError:
    error_logger = None

# Import rate limiting
try:
    from app.decorators.auth_decorators import rate_limit
except ImportError:
    import functools
    def rate_limit(requests_per_minute=60):
        def decorator(f):
            @functools.wraps(f)
            def decorated_function(*args, **kwargs):
                return f(*args, **kwargs)
            return decorated_function
        return decorator

@public_api_bp.route('/health', methods=['GET'])
def health_check():
    """Public API health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'app_module': 'public_api',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'endpoints': [
                '/api/v1/public/health',
                '/api/v1/public/contact',
                '/api/v1/public/pages',
                '/api/v1/public/documentation',
                '/api/v1/public/whitepaper'
            ]
        })
    except Exception as e:
        logger.error(f"Public API health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@public_api_bp.route('/contact', methods=['POST'])
@rate_limit(requests_per_minute=3)
def submit_contact():
    """Handle contact form submission via API"""
    try:
        # Get JSON data
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email', 'subject', 'message']
        form_data = {}
        missing_fields = []
        
        for field in required_fields:
            value = data.get(field, '').strip()
            if not value:
                missing_fields.append(field)
            else:
                form_data[field] = value
        
        if missing_fields:
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Optional fields
        form_data['phone'] = data.get('phone', '').strip()
        form_data['company'] = data.get('company', '').strip()
        
        # Email validation
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, form_data['email']):
            return jsonify({
                'status': 'error',
                'message': 'Please enter a valid email address'
            }), 400
        
        # Log contact submission
        logger.info(f"API Contact form submission: {form_data['email']} - {form_data['subject']}")
        
        # Store contact inquiry data
        contact_data = {
            **form_data,
            'timestamp': datetime.now().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'submission_method': 'api'
        }
        
        # Log the contact inquiry
        if error_logger:
            try:
                error_logger.log_security_event(
                    message="API contact form submitted",
                    event_type="api_contact_form_submission",
                    context=contact_data
                )
            except Exception as log_error:
                logger.warning(f"Failed to log security event: {log_error}")
        
        return jsonify({
            'status': 'success',
            'message': 'Thank you for your message. We will respond within 2 hours.',
            'data': {
                'submission_id': f"contact_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'timestamp': contact_data['timestamp']
            }
        })
        
    except Exception as e:
        logger.error(f"Error processing API contact form: {e}")
        if error_logger:
            try:
                error_logger.log_error(
                    message=f"Failed to process API contact form: {str(e)}",
                    error_type="api_contact_form_error",
                    context={
                        'route': 'public_api.submit_contact',
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

@public_api_bp.route('/pages', methods=['GET'])
def get_pages():
    """Get list of available public pages"""
    try:
        pages = [
            {
                'id': 'about',
                'title': 'About Us',
                'url': '/public/about',
                'description': 'Learn about NVC Banking Platform'
            },
            {
                'id': 'services',
                'title': 'Services',
                'url': '/public/services',
                'description': 'Our banking and financial services'
            },
            {
                'id': 'contact',
                'title': 'Contact',
                'url': '/public/contact',
                'description': 'Get in touch with our team'
            },
            {
                'id': 'privacy_policy',
                'title': 'Privacy Policy',
                'url': '/public/privacy-policy',
                'description': 'Our privacy policy and data protection'
            },
            {
                'id': 'terms_of_service',
                'title': 'Terms of Service',
                'url': '/public/terms-of-service',
                'description': 'Terms and conditions of service'
            },
            {
                'id': 'getting_started',
                'title': 'Getting Started',
                'url': '/public/getting-started',
                'description': 'Getting started guide'
            },
            {
                'id': 'user_guide',
                'title': 'User Guide',
                'url': '/public/user-guide',
                'description': 'Complete user guide'
            },
            {
                'id': 'faq',
                'title': 'FAQ',
                'url': '/public/faq',
                'description': 'Frequently asked questions'
            },
            {
                'id': 'documentation',
                'title': 'Documentation',
                'url': '/public/documentation',
                'description': 'Technical documentation'
            },
            {
                'id': 'nvct_whitepaper',
                'title': 'NVCT Whitepaper',
                'url': '/public/nvct-whitepaper',
                'description': 'NVCT Stablecoin technical whitepaper'
            }
        ]
        
        return jsonify({
            'status': 'success',
            'data': {
                'pages': pages,
                'total_pages': len(pages),
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting pages list: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve pages list'
        }), 500

@public_api_bp.route('/documentation', methods=['GET'])
def get_documentation():
    """Get documentation structure"""
    try:
        documentation = {
            'api_documentation': {
                'title': 'API Documentation',
                'description': 'Complete API reference guide',
                'url': '/public/api-documentation',
                'sections': [
                    'Authentication',
                    'Endpoints',
                    'Request/Response Format',
                    'Error Codes',
                    'Rate Limiting',
                    'Examples'
                ]
            },
            'user_guide': {
                'title': 'User Guide',
                'description': 'Complete user guide for banking platform',
                'url': '/public/user-guide',
                'sections': [
                    'Getting Started',
                    'Account Management',
                    'Transfers',
                    'Cards & Payments',
                    'Security',
                    'Troubleshooting'
                ]
            },
            'developer_docs': {
                'title': 'Developer Documentation',
                'description': 'Technical documentation for developers',
                'url': '/public/documentation',
                'sections': [
                    'SDK Installation',
                    'Integration Guide',
                    'Webhooks',
                    'Code Examples',
                    'Best Practices'
                ]
            }
        }
        
        return jsonify({
            'status': 'success',
            'data': {
                'documentation': documentation,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting documentation: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve documentation'
        }), 500

@public_api_bp.route('/whitepaper', methods=['GET'])
def get_whitepaper_info():
    """Get NVCT whitepaper information"""
    try:
        whitepaper_info = {
            'title': 'NVCT Stablecoin Technical Whitepaper',
            'version': '2.0',
            'release_date': '2024-12-15',
            'description': 'Comprehensive technical documentation for NVCT stablecoin',
            'url': '/public/nvct-whitepaper',
            'download_url': '/public/download-whitepaper',
            'sections': [
                'Executive Summary',
                'Technical Architecture',
                'Blockchain Integration',
                'Smart Contract Design',
                'Security Framework',
                'Governance Model',
                'Economic Model',
                'Risk Management',
                'Compliance Framework',
                'Future Roadmap'
            ],
            'key_features': [
                '$30 Trillion Total Supply',
                '189% Over-collateralization',
                'Multi-blockchain Support',
                'Institutional Grade Security',
                'Regulatory Compliance',
                'Cross-chain Interoperability'
            ],
            'networks': [
                'Ethereum',
                'Polygon',
                'Binance Smart Chain',
                'Arbitrum',
                'Optimism'
            ]
        }
        
        return jsonify({
            'status': 'success',
            'data': {
                'whitepaper': whitepaper_info,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting whitepaper info: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve whitepaper information'
        }), 500

@public_api_bp.route('/services', methods=['GET'])
def get_services():
    """Get available banking services"""
    try:
        services = [
            {
                'id': 'digital_banking',
                'title': 'Digital Banking',
                'description': 'Complete digital banking platform',
                'features': [
                    'Account Management',
                    'Online Transfers',
                    'Mobile Banking',
                    'Digital Payments'
                ]
            },
            {
                'id': 'blockchain_services',
                'title': 'Blockchain Services',
                'description': 'Blockchain-enabled financial services',
                'features': [
                    'NVCT Stablecoin',
                    'Smart Contracts',
                    'Cross-chain Transfers',
                    'DeFi Integration'
                ]
            },
            {
                'id': 'institutional_banking',
                'title': 'Institutional Banking',
                'description': 'Enterprise banking solutions',
                'features': [
                    'Corporate Accounts',
                    'Treasury Management',
                    'Trade Finance',
                    'Risk Management'
                ]
            },
            {
                'id': 'security_services',
                'title': 'Security Services',
                'description': 'Advanced security and compliance',
                'features': [
                    'Multi-factor Authentication',
                    'Fraud Detection',
                    'Compliance Monitoring',
                    'Risk Assessment'
                ]
            }
        ]
        
        return jsonify({
            'status': 'success',
            'data': {
                'services': services,
                'total_services': len(services),
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting services: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve services'
        }), 500

@public_api_bp.route('/news', methods=['GET'])
def get_news():
    """Get latest news and updates"""
    try:
        news = [
            {
                'id': 'nvct_launch',
                'title': 'NVCT Stablecoin Launch',
                'summary': 'NVC Banking Platform launches institutional-grade stablecoin',
                'date': '2024-12-15',
                'category': 'Product Launch',
                'url': '/public/news/nvct-launch'
            },
            {
                'id': 'blockchain_integration',
                'title': 'Multi-Blockchain Integration',
                'summary': 'Platform now supports multiple blockchain networks',
                'date': '2024-12-10',
                'category': 'Technology',
                'url': '/public/news/blockchain-integration'
            },
            {
                'id': 'security_upgrade',
                'title': 'Enhanced Security Framework',
                'summary': 'New security features and compliance updates',
                'date': '2024-12-05',
                'category': 'Security',
                'url': '/public/news/security-upgrade'
            }
        ]
        
        return jsonify({
            'status': 'success',
            'data': {
                'news': news,
                'total_articles': len(news),
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting news: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve news'
        }), 500

# Error handlers
@public_api_bp.errorhandler(404)
def api_not_found(error):
    """Handle 404 errors for API"""
    return jsonify({
        'status': 'error',
        'message': 'API endpoint not found',
        'error_code': 'NOT_FOUND'
    }), 404

@public_api_bp.errorhandler(500)
def api_internal_error(error):
    """Handle 500 errors for API"""
    logger.error(f"500 error in public API: {str(error)}")
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'error_code': 'INTERNAL_ERROR'
    }), 500

@public_api_bp.errorhandler(400)
def api_bad_request(error):
    """Handle 400 errors for API"""
    return jsonify({
        'status': 'error',
        'message': 'Bad request',
        'error_code': 'BAD_REQUEST'
    }), 400

@public_api_bp.errorhandler(429)
def api_rate_limit_exceeded(error):
    """Handle 429 errors for API"""
    return jsonify({
        'status': 'error',
        'message': 'Rate limit exceeded. Please try again later.',
        'error_code': 'RATE_LIMIT_EXCEEDED'
    }), 429

# API module information
API_MODULE_INFO = {
    'name': 'Public API Module',
    'version': '1.0.0',
    'description': 'RESTful API endpoints for public module',
    'endpoints': [
        {
            'path': '/api/v1/public/health',
            'methods': ['GET'],
            'description': 'Health check endpoint'
        },
        {
            'path': '/api/v1/public/contact',
            'methods': ['POST'],
            'description': 'Submit contact form'
        },
        {
            'path': '/api/v1/public/pages',
            'methods': ['GET'],
            'description': 'Get available public pages'
        },
        {
            'path': '/api/v1/public/documentation',
            'methods': ['GET'],
            'description': 'Get documentation structure'
        },
        {
            'path': '/api/v1/public/whitepaper',
            'methods': ['GET'],
            'description': 'Get NVCT whitepaper information'
        },
        {
            'path': '/api/v1/public/services',
            'methods': ['GET'],
            'description': 'Get available banking services'
        },
        {
            'path': '/api/v1/public/news',
            'methods': ['GET'],
            'description': 'Get latest news and updates'
        }
    ],
    'rate_limits': {
        'contact': '3 requests/minute',
        'default': '60 requests/minute'
    },
    'authentication': 'Not required for public endpoints',
    'status': 'active'
}

def get_api_module_info():
    """Get API module information"""
    return API_MODULE_INFO