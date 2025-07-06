"""
Binance Integration Module Routes
OAuth 2.0 authentication and API integration with Binance
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from flask_login import login_required, current_user
import logging
from urllib.parse import urlparse, parse_qs
import json

# Import services
from .services import BinanceOAuthService, BinanceAPIService, BinanceIntegrationService

# Create blueprint
binance_bp = Blueprint(
    'binance',
    __name__,
    url_prefix='/binance-integration',
    template_folder='templates',
    static_folder='static'
)

logger = logging.getLogger(__name__)

@binance_bp.route('/')
@login_required
def binance_dashboard():
    """Binance Integration Dashboard"""
    try:
        logger.info(f"User {current_user.username} accessing Binance integration dashboard")
        
        service = BinanceIntegrationService()
        dashboard_data = service.get_dashboard_data()
        
        return render_template(
            'binance_dashboard.html',
            dashboard_data=dashboard_data,
            page_title="Binance Integration"
        )
    except Exception as e:
        logger.error(f"Error loading Binance dashboard: {e}")
        flash('Error loading Binance integration dashboard', 'error')
        return redirect(url_for('dashboard.dashboard_home'))

@binance_bp.route('/connect')
@login_required
def connect_binance():
    """Initiate Binance OAuth connection"""
    try:
        logger.info(f"User {current_user.username} initiating Binance OAuth connection")
        
        # Get requested scopes from form or use defaults
        scopes = request.args.getlist('scopes') or ['user:openId', 'user:email']
        
        oauth_service = BinanceOAuthService()
        auth_data = oauth_service.generate_authorization_url(scopes)
        
        # Store OAuth data in session for verification
        session['binance_oauth_state'] = auth_data['state']
        session['binance_code_verifier'] = auth_data['code_verifier']
        session['binance_scopes_requested'] = auth_data['scopes_requested']
        
        logger.info(f"Redirecting user {current_user.username} to Binance OAuth: {auth_data['authorization_url']}")
        
        return redirect(auth_data['authorization_url'])
        
    except Exception as e:
        logger.error(f"Error initiating Binance OAuth: {e}")
        flash(f'Error connecting to Binance: {str(e)}', 'error')
        return redirect(url_for('binance.binance_dashboard'))

@binance_bp.route('/callback')
@login_required
def oauth_callback():
    """Handle OAuth callback from Binance"""
    try:
        logger.info(f"Processing Binance OAuth callback for user {current_user.username}")
        
        # Get authorization code and state from callback
        authorization_code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        # Handle OAuth errors
        if error:
            logger.error(f"OAuth error: {error}")
            flash(f'Binance authorization failed: {error}', 'error')
            return redirect(url_for('binance.binance_dashboard'))
        
        if not authorization_code:
            logger.error("No authorization code received")
            flash('No authorization code received from Binance', 'error')
            return redirect(url_for('binance.binance_dashboard'))
        
        # Verify state parameter for CSRF protection
        stored_state = session.get('binance_oauth_state')
        if not state or state != stored_state:
            logger.error(f"State mismatch: received {state}, expected {stored_state}")
            flash('Invalid state parameter - potential CSRF attack', 'error')
            return redirect(url_for('binance.binance_dashboard'))
        
        # Exchange code for tokens
        oauth_service = BinanceOAuthService()
        code_verifier = session.get('binance_code_verifier')
        
        token_response = oauth_service.exchange_code_for_tokens(
            authorization_code, 
            code_verifier
        )
        
        # Validate the received tokens
        api_service = BinanceAPIService()
        validation_result = api_service.validate_token(token_response['access_token'])
        
        if validation_result['valid']:
            # Store tokens securely (in production, use encrypted storage)
            session['binance_access_token'] = token_response['access_token']
            session['binance_refresh_token'] = token_response.get('refresh_token')
            session['binance_token_expires_at'] = token_response['expires_at']
            session['binance_user_id'] = validation_result['user_id']
            session['binance_email'] = validation_result.get('email')
            
            # Clear OAuth session data
            session.pop('binance_oauth_state', None)
            session.pop('binance_code_verifier', None)
            
            logger.info(f"Successfully connected Binance account for user {current_user.username}")
            flash('Successfully connected to Binance!', 'success')
        else:
            logger.error(f"Token validation failed: {validation_result.get('error')}")
            flash('Failed to validate Binance connection', 'error')
        
        return redirect(url_for('binance.binance_dashboard'))
        
    except Exception as e:
        logger.error(f"Error processing OAuth callback: {e}")
        flash(f'Error processing Binance connection: {str(e)}', 'error')
        return redirect(url_for('binance.binance_dashboard'))

@binance_bp.route('/disconnect', methods=['POST'])
@login_required
def disconnect_binance():
    """Disconnect Binance account"""
    try:
        logger.info(f"User {current_user.username} disconnecting Binance account")
        
        access_token = session.get('binance_access_token')
        
        if access_token:
            # Revoke access token
            oauth_service = BinanceOAuthService()
            revocation_success = oauth_service.revoke_access_token(access_token)
            
            if revocation_success:
                logger.info("Successfully revoked Binance access token")
            else:
                logger.warning("Failed to revoke Binance access token on server")
        
        # Clear all Binance session data
        binance_keys = [key for key in session.keys() if key.startswith('binance_')]
        for key in binance_keys:
            session.pop(key, None)
        
        flash('Binance account disconnected successfully', 'success')
        
        return redirect(url_for('binance.binance_dashboard'))
        
    except Exception as e:
        logger.error(f"Error disconnecting Binance: {e}")
        flash(f'Error disconnecting Binance: {str(e)}', 'error')
        return redirect(url_for('binance.binance_dashboard'))

@binance_bp.route('/user-info')
@login_required
def get_user_info():
    """Get Binance user information"""
    try:
        access_token = session.get('binance_access_token')
        
        if not access_token:
            return jsonify({
                'status': 'error',
                'error': 'No Binance connection found'
            }), 401
        
        api_service = BinanceAPIService()
        user_info = api_service.get_user_info(access_token)
        
        return jsonify(user_info)
        
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@binance_bp.route('/trading-interface')
@login_required
def trading_interface():
    """Professional trading interface with real-time price charts and order management"""
    try:
        access_token = session.get('binance_access_token')
        
        if not access_token:
            flash('Please connect your Binance account first', 'warning')
            return redirect(url_for('binance.binance_dashboard'))
            
        api_service = BinanceAPIService()
        trading_data = api_service.get_trading_data(access_token)
        
        return render_template('binance_integration/trading_interface.html',
                             trading_data=trading_data,
                             page_title='Trading Interface')
        
    except Exception as e:
        logger.error(f"Error loading trading interface: {e}")
        flash('Error loading trading interface', 'error')
        return redirect(url_for('binance.binance_dashboard'))

@binance_bp.route('/api-settings')
@login_required
def api_settings():
    """API settings management with security controls and permission management"""
    try:
        access_token = session.get('binance_access_token')
        
        if not access_token:
            flash('Please connect your Binance account first', 'warning')
            return redirect(url_for('binance.binance_dashboard'))
            
        api_service = BinanceAPIService()
        api_settings_data = api_service.get_api_settings(access_token)
        
        return render_template('binance_integration/api_settings.html',
                             api_settings=api_settings_data,
                             page_title='API Settings')
        
    except Exception as e:
        logger.error(f"Error loading API settings: {e}")
        flash('Error loading API settings', 'error')
        return redirect(url_for('binance.binance_dashboard'))

@binance_bp.route('/main-dashboard')
@login_required
def binance_main_dashboard():
    """Main Binance dashboard using orphaned template"""
    try:
        access_token = session.get('binance_access_token')
        
        if not access_token:
            flash('Please connect your Binance account first', 'warning')
            return redirect(url_for('binance.binance_dashboard'))
            
        api_service = BinanceAPIService()
        dashboard_data = api_service.get_dashboard_data(access_token)
        
        return render_template('binance_dashboard.html',
                             dashboard_data=dashboard_data,
                             page_title='Binance Main Dashboard',
                             user=current_user)
        
    except Exception as e:
        logger.error(f"Error loading main dashboard: {e}")
        flash('Error loading main dashboard', 'error')
        return redirect(url_for('binance.binance_dashboard'))

@binance_bp.route('/connection-status')
@login_required
def connection_status():
    """Get Binance connection status"""
    try:
        access_token = session.get('binance_access_token')
        
        if not access_token:
            return jsonify({
                'connected': False,
                'status': 'not_connected'
            })
        
        # Validate current token
        api_service = BinanceAPIService()
        validation_result = api_service.validate_token(access_token)
        
        if validation_result['valid']:
            return jsonify({
                'connected': True,
                'status': 'connected',
                'user_id': validation_result['user_id'],
                'email': validation_result.get('email'),
                'token_expires_at': session.get('binance_token_expires_at'),
                'validated_at': validation_result['validated_at']
            })
        else:
            # Token is invalid, clear session
            binance_keys = [key for key in session.keys() if key.startswith('binance_')]
            for key in binance_keys:
                session.pop(key, None)
            
            return jsonify({
                'connected': False,
                'status': 'token_invalid',
                'error': validation_result.get('error')
            })
        
    except Exception as e:
        logger.error(f"Error checking connection status: {e}")
        return jsonify({
            'connected': False,
            'status': 'error',
            'error': str(e)
        }), 500

# API Routes
@binance_bp.route('/api/integration-status')
@login_required
def api_integration_status():
    """API endpoint for integration status"""
    try:
        service = BinanceIntegrationService()
        status = service.get_integration_status()
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting integration status: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@binance_bp.route('/api/refresh-token', methods=['POST'])
@login_required
def api_refresh_token():
    """Refresh Binance access token"""
    try:
        refresh_token = session.get('binance_refresh_token')
        
        if not refresh_token:
            return jsonify({
                'status': 'error',
                'error': 'No refresh token available'
            }), 401
        
        oauth_service = BinanceOAuthService()
        token_response = oauth_service.refresh_access_token(refresh_token)
        
        # Update session with new tokens
        session['binance_access_token'] = token_response['access_token']
        session['binance_refresh_token'] = token_response.get('refresh_token', refresh_token)
        session['binance_token_expires_at'] = token_response['expires_at']
        
        return jsonify({
            'status': 'success',
            'message': 'Token refreshed successfully',
            'expires_at': token_response['expires_at']
        })
        
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@binance_bp.route('/api/health')
def health_check():
    """Binance integration module health check"""
    return jsonify({
        'status': 'healthy',
        'app_module': 'binance_integration',
        'version': '1.0.0',
        'timestamp': '2025-07-03T17:30:00Z',
        'oauth_endpoints': {
            'authorization': 'https://accounts.binance.com/en/oauth/authorize',
            'token': 'https://accounts.binance.com/oauth/token',
            'api': 'https://www.binanceapis.com/oauth-api/v1'
        }
    })

# Additional health endpoints can be added here if needed

# Error handlers
@binance_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors within Binance integration module"""
    return render_template('404.html'), 404

@binance_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors within Binance integration module"""
    logger.error(f"Internal error in Binance integration module: {error}")
    return render_template('500.html'), 500

# API Health endpoint
@binance_bp.route('/api/health', methods=['GET'])
def api_health_check():
    """API health check endpoint for Binance Integration module"""
    try:
        return jsonify({
            'status': 'healthy',
            'app_module': 'binance_integration',
            'version': '1.0.0',
            'services': {
                'oauth': 'available',
                'api': 'available'
            },
            'endpoints': [
                '/binance/',
                '/binance/connect',
                '/binance/callback',
                '/binance/disconnect',
                '/binance/user-info',
                '/binance/status',
                '/binance/api/health',
                '/binance/api/status'
            ]
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'app_module': 'binance_integration',
            'error': str(e)
        }), 500

# API Status endpoint
@binance_bp.route('/api/status', methods=['GET'])
def api_status_check():
    """Detailed status endpoint for Binance Integration module"""
    try:
        service = BinanceIntegrationService()
        integration_status = service.get_integration_status()
        
        return jsonify({
            'status': 'operational',
            'app_module': 'binance_integration',
            'version': '1.0.0',
            'integration_status': integration_status,
            'oauth_service': {
                'status': 'ready',
                'client_configured': integration_status['has_credentials'],
                'flows_supported': integration_status['oauth_flows_supported']
            },
            'api_service': {
                'status': 'ready',
                'endpoints_available': len(integration_status['api_endpoints'])
            },
            'timestamp': integration_status['last_checked']
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'app_module': 'binance_integration',
            'error': str(e)
        }), 500