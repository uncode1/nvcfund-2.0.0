"""
Enhanced Authentication Routes with MFA and Security Gap Closure
Implements comprehensive authentication security while maintaining UI/UX
"""

from flask import Blueprint, request, render_template, redirect, flash, session, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from typing import List
import logging
import json

from .config import AuthConfig
from .services import AuthService
from .models import User
from modules.core.extensions import db, csrf
from modules.core.enhanced_security import enhanced_security
from modules.core.mfa_system import mfa_system

logger = logging.getLogger(__name__)

# Enhanced Auth Blueprint
enhanced_auth_bp = Blueprint('enhanced_auth', __name__, url_prefix='/auth', template_folder='templates')

@enhanced_auth_bp.route('/setup-mfa', methods=['GET', 'POST'])
@login_required
@enhanced_security.enhanced_session_security
@enhanced_security.audit_log_decorator('mfa_setup')
def setup_mfa():
    """
    Set up Multi-Factor Authentication for user
    Maintains existing UI while adding security layer
    """
    if request.method == 'GET':
        # Check if MFA is already configured
        if hasattr(current_user, 'mfa_config') and current_user.mfa_config:
            mfa_config = json.loads(current_user.mfa_config) if isinstance(current_user.mfa_config, str) else current_user.mfa_config
            mfa_status = mfa_system.get_mfa_status(mfa_config)
            
            if mfa_status['enabled']:
                flash('MFA is already configured for your account', 'info')
                return redirect(url_for('dashboard.main_dashboard'))
        
        # Generate TOTP setup data
        setup_data = mfa_system.setup_totp_for_user(current_user.id, current_user.username)
        
        if not setup_data['success']:
            flash('Failed to setup MFA. Please try again.', 'error')
            return redirect(url_for('dashboard.main_dashboard'))
        
        # Store temporary MFA config in session
        session['temp_mfa_setup'] = setup_data['mfa_config']
        
        return render_template('auth/mfa_setup.html', 
                             qr_code=setup_data['qr_code'],
                             manual_key=setup_data['manual_entry_key'],
                             backup_codes=setup_data['backup_codes'])
    
    elif request.method == 'POST':
        # Validate setup with verification token
        verification_token = request.form.get('verification_token', '').strip()
        
        if not verification_token:
            flash('Please enter the verification code from your authenticator app', 'error')
            return redirect(url_for('enhanced_auth.setup_mfa'))
        
        # Get temp MFA config from session
        temp_mfa_config = session.get('temp_mfa_setup')
        if not temp_mfa_config:
            flash('MFA setup session expired. Please start over.', 'error')
            return redirect(url_for('enhanced_auth.setup_mfa'))
        
        # Verify the token
        secret = temp_mfa_config.get('totp_secret')
        if mfa_system.validate_mfa_setup(secret, verification_token):
            # Save MFA configuration to user
            temp_mfa_config['is_verified'] = True
            temp_mfa_config['verified_date'] = datetime.utcnow().isoformat()
            
            current_user.mfa_config = json.dumps(temp_mfa_config)
            current_user.mfa_enabled = True
            db.session.commit()
            
            # Clear session
            session.pop('temp_mfa_setup', None)
            
            flash('Multi-Factor Authentication has been successfully enabled!', 'success')
            logger.info(f"MFA enabled for user {current_user.id}")
            
            return redirect(url_for('dashboard.main_dashboard'))
        else:
            flash('Invalid verification code. Please try again.', 'error')
            return redirect(url_for('enhanced_auth.setup_mfa'))

@enhanced_auth_bp.route('/mfa-verify', methods=['GET', 'POST'])
def mfa_verify():
    """
    MFA verification during login process
    """
    # Check if user is in MFA verification state
    if 'mfa_user_id' not in session:
        flash('Authentication session expired', 'error')
        return redirect(url_for('auth.login'))
    
    user_id = session['mfa_user_id']
    user = User.query.get(user_id)
    
    if not user or not user.mfa_enabled:
        session.pop('mfa_user_id', None)
        flash('Authentication error', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'GET':
        return render_template('auth/mfa_verify.html', username=user.username)
    
    elif request.method == 'POST':
        mfa_token = request.form.get('mfa_token', '').strip()
        use_backup_code = request.form.get('use_backup_code') == 'true'
        
        if not mfa_token:
            flash('Please enter your authentication code', 'error')
            return render_template('auth/mfa_verify.html', username=user.username)
        
        # Get user's MFA configuration
        mfa_config = json.loads(user.mfa_config) if isinstance(user.mfa_config, str) else user.mfa_config
        
        verification_success = False
        
        if use_backup_code:
            # Verify backup code
            backup_codes = mfa_config.get('backup_codes', [])
            success, remaining_codes = mfa_system.verify_backup_code(backup_codes, mfa_token)
            
            if success:
                # Update backup codes
                mfa_config['backup_codes'] = remaining_codes
                user.mfa_config = json.dumps(mfa_config)
                db.session.commit()
                verification_success = True
                logger.info(f"Backup code used for user {user_id}")
        else:
            # Verify TOTP token
            secret = mfa_config.get('totp_secret')
            verification_success = mfa_system.verify_totp_token(secret, mfa_token)
        
        if verification_success:
            # Complete login process
            login_user(user, remember=session.get('remember_me', False))
            session.permanent = True
            
            # Clear MFA session data
            session.pop('mfa_user_id', None)
            session.pop('remember_me', None)
            
            # Update login tracking
            user.last_login = datetime.utcnow()
            user.login_count = (user.login_count or 0) + 1
            db.session.commit()
            
            logger.info(f"MFA verification successful for user {user_id}")
            
            # Redirect to appropriate dashboard
            from .services import AuthService
            auth_service = AuthService()
            dashboard_url = auth_service.determine_dashboard_redirect(user.username, user.role)
            
            return redirect(dashboard_url)
        else:
            flash('Invalid authentication code. Please try again.', 'error')
            return render_template('auth/mfa_verify.html', username=user.username)

@enhanced_auth_bp.route('/password-strength-check', methods=['POST'])
@csrf.exempt  # Allow AJAX calls
def password_strength_check():
    """
    AJAX endpoint for real-time password strength checking
    """
    password = request.json.get('password', '')
    
    if not password:
        return jsonify({'valid': False, 'strength_score': 0, 'errors': ['Password is required']})
    
    # Use enhanced security framework for validation
    validation_result = enhanced_security.validate_banking_password(password)
    
    return jsonify(validation_result)

@enhanced_auth_bp.route('/validate-input', methods=['POST'])
@csrf.exempt  # Allow AJAX calls
def validate_input():
    """
    AJAX endpoint for comprehensive input validation
    """
    data = request.json.get('data', {})
    validation_rules = request.json.get('rules', {})
    
    if not data or not validation_rules:
        return jsonify({'valid': False, 'errors': {'general': 'Invalid request data'}})
    
    # Use enhanced security framework for validation
    validation_result = enhanced_security.comprehensive_input_validation(data, validation_rules)
    
    return jsonify(validation_result)

@enhanced_auth_bp.route('/mfa-status')
@login_required
@enhanced_security.enhanced_session_security
def mfa_status():
    """
    Get MFA status for current user
    """
    if not hasattr(current_user, 'mfa_config') or not current_user.mfa_config:
        return jsonify({
            'enabled': False,
            'setup_required': True
        })
    
    mfa_config = json.loads(current_user.mfa_config) if isinstance(current_user.mfa_config, str) else current_user.mfa_config
    status = mfa_system.get_mfa_status(mfa_config)
    
    return jsonify(status)

@enhanced_auth_bp.route('/regenerate-backup-codes', methods=['POST'])
@login_required
@enhanced_security.enhanced_session_security
@enhanced_security.audit_log_decorator('mfa_backup_codes_regenerated')
def regenerate_backup_codes():
    """
    Regenerate backup codes for user
    """
    if not current_user.mfa_enabled:
        return jsonify({'success': False, 'error': 'MFA not enabled'})
    
    # Generate new backup codes
    new_codes = mfa_system.regenerate_backup_codes(current_user.id)
    
    if new_codes:
        # Update user's MFA configuration
        mfa_config = json.loads(current_user.mfa_config) if isinstance(current_user.mfa_config, str) else current_user.mfa_config
        mfa_config['backup_codes'] = new_codes
        mfa_config['backup_codes_regenerated'] = datetime.utcnow().isoformat()
        
        current_user.mfa_config = json.dumps(mfa_config)
        db.session.commit()
        
        logger.info(f"Backup codes regenerated for user {current_user.id}")
        
        return jsonify({
            'success': True,
            'backup_codes': new_codes
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to regenerate backup codes'
        })

# Enhanced login route that integrates with existing auth
@enhanced_auth_bp.route('/enhanced-login', methods=['POST'])
def enhanced_login():
    """
    Enhanced login with comprehensive validation and MFA
    Integrates with existing login while adding security layers
    """
    # Input validation
    form_data = {
        'username': request.form.get('username', ''),
        'password': request.form.get('password', '')
    }
    
    validation_rules = {
        'username': 'username',
        'password': 'password'
    }
    
    validation_result = enhanced_security.comprehensive_input_validation(form_data, validation_rules)
    
    if not validation_result['valid']:
        for field, error in validation_result['errors'].items():
            flash(f'{field.title()}: {error}', 'error')
        return redirect(url_for('auth.login'))
    
    username = validation_result['data']['username']
    password = validation_result['data']['password']
    remember_me = request.form.get('remember_me') is not None
    
    try:
        # Authenticate user
        user = User.query.filter_by(username=username).first()
        
        if user and user.is_active and check_password_hash(user.password_hash, password):
            # Check if MFA is enabled
            if user.mfa_enabled and user.mfa_config:
                # Store user ID for MFA verification
                session['mfa_user_id'] = user.id
                session['remember_me'] = remember_me
                
                logger.info(f"User {username} requires MFA verification")
                return redirect(url_for('enhanced_auth.mfa_verify'))
            else:
                # Standard login without MFA
                login_user(user, remember=remember_me)
                session.permanent = True
                
                # Update login tracking
                user.last_login = datetime.utcnow()
                user.login_count = (user.login_count or 0) + 1
                db.session.commit()
                
                logger.info(f"Enhanced login successful for user: {username}")
                
                # Role-based dashboard redirection
                from .services import AuthService
                auth_service = AuthService()
                dashboard_url = auth_service.determine_dashboard_redirect(username, user.role)
                
                return redirect(dashboard_url)
        else:
            logger.warning(f"Enhanced login failed for username: {username}")
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
            
    except Exception as e:
        logger.error(f"Enhanced login error for {username}: {e}")
        flash('Login failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))

# Apply security headers to all routes in this blueprint
@enhanced_auth_bp.after_request
def apply_security_headers(response):
    """Apply enhanced security headers to auth routes"""
    return enhanced_security.security_headers_middleware(response)