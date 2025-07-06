"""
Auth Module Routes - Self-contained Authentication System
Comprehensive authentication routes with role-based redirection logic
"""

from flask import Blueprint, request, render_template, redirect, flash, session, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import logging
import random
import string

from .config import AuthConfig
from .services import AuthService
from .models import User
from modules.core.extensions import db, csrf, login_manager
from modules.communications.services import EmailService, PersonalizedMessageService

# Configure logging
logger = logging.getLogger(__name__)

# Create Auth Module Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates')

# Initialize auth service
auth_service = AuthService()

# Configure login manager user loader
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    try:
        return User.query.get(user_id)
    except Exception as e:
        logger.error(f"Error loading user {user_id}: {e}")
        return None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Modular Authentication Login Route
    Handles user authentication with role-based dashboard redirection
    """
    logger.info("🔐 Auth Module: Login route accessed - Method: %s", request.method)
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') is not None
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('auth/modular_auth_login.html')
        
        try:
            # Authenticate user
            user = User.query.filter_by(username=username).first()
            
            if user and user.is_active and check_password_hash(user.password_hash, password):
                # Update login tracking
                user.last_login = datetime.utcnow()
                user.login_count = (user.login_count or 0) + 1
                db.session.commit()
                
                # Login user with Flask-Login
                login_user(user, remember=remember_me)
                session.permanent = True
                
                logger.info("✅ Auth Module: Successful login for user: %s (Role: %s)", username, user.role)
                
                # Role-based dashboard redirection
                dashboard_url = auth_service.determine_dashboard_redirect(username, user.role)
                logger.info("🔀 Auth Module: Redirecting user %s to: %s", username, dashboard_url)
                
                return redirect(dashboard_url)
                
            else:
                logger.warning("❌ Auth Module: Failed login attempt for username: %s", username)
                flash('Invalid username or password', 'error')
                
        except Exception as e:
            logger.error("❌ Auth Module: Authentication error: %s", str(e))
            flash('Authentication service unavailable. Please try again later.', 'error')
    
    return render_template('auth/modular_auth_login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Modular Authentication Logout Route
    Securely logs out user and clears session
    """
    username = current_user.username if current_user.is_authenticated else 'Unknown'
    logger.info("🚪 Auth Module: Logout requested for user: %s", username)
    
    logout_user()
    session.clear()
    
    flash('You have been successfully logged out', 'success')
    logger.info("✅ Auth Module: User %s successfully logged out", username)
    
    return redirect(AuthConfig.POST_LOGOUT_REDIRECT)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Modular Authentication Registration Route
    Handles new user registration with KYC compliance
    """
    logger.info("📝 Auth Module: Registration route accessed - Method: %s", request.method)
    
    if request.method == 'POST':
        try:
            # Extract registration data
            registration_data = {
                'username': request.form.get('username'),
                'email': request.form.get('email'),
                'password': request.form.get('password'),
                'confirm_password': request.form.get('confirm_password'),
                'first_name': request.form.get('first_name'),
                'last_name': request.form.get('last_name'),
                'phone_number': request.form.get('phone_number'),
                'date_of_birth': request.form.get('date_of_birth'),
                'account_type': request.form.get('account_type', 'USER')
            }
            
            # Validate registration data
            validation_result = auth_service.validate_registration(registration_data)
            if not validation_result['valid']:
                for error in validation_result['errors']:
                    flash(error, 'error')
                return render_template('auth/modular_auth_register.html')
            
            # Create new user
            user_result = auth_service.create_user(registration_data)
            if user_result['success']:
                logger.info("✅ Auth Module: New user registered: %s", registration_data['username'])
                flash('Registration successful! Please log in.', 'success')
                return redirect(AuthConfig.POST_REGISTER_REDIRECT)
            else:
                flash(user_result['error'], 'error')
                
        except Exception as e:
            logger.error("❌ Auth Module: Registration error: %s", str(e))
            flash('Registration service unavailable. Please try again later.', 'error')
    
    return render_template('auth/modular_auth_register.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Modular Authentication Forgot Password Route
    Handles password reset requests
    """
    logger.info("🔄 Auth Module: Forgot password route accessed - Method: %s", request.method)
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Email address is required', 'error')
            return render_template('auth/modular_auth_forgot_password.html')
        
        try:
            result = auth_service.initiate_password_reset(email)
            if result['success']:
                flash('Password reset instructions have been sent to your email', 'success')
                logger.info("✅ Auth Module: Password reset initiated for email: %s", email)
            else:
                flash(result['error'], 'error')
                
        except Exception as e:
            logger.error("❌ Auth Module: Forgot password error: %s", str(e))
            flash('Password reset service unavailable. Please try again later.', 'error')
    
    return render_template('auth/modular_auth_forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Modular Authentication Reset Password Route
    Handles password reset with token validation
    """
    logger.info("🔐 Auth Module: Reset password route accessed for token: %s", token[:8] + "...")
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password or not confirm_password:
            flash('Both password fields are required', 'error')
            return render_template('auth/modular_auth_reset_password.html', token=token)
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/modular_auth_reset_password.html', token=token)
        
        try:
            result = auth_service.reset_password_with_token(token, new_password)
            if result['success']:
                flash('Password successfully reset! Please log in with your new password.', 'success')
                logger.info("✅ Auth Module: Password reset completed for token: %s", token[:8] + "...")
                return redirect(AuthConfig.LOGIN_URL)
            else:
                flash(result['error'], 'error')
                
        except Exception as e:
            logger.error("❌ Auth Module: Password reset error: %s", str(e))
            flash('Password reset service unavailable. Please try again later.', 'error')
    
    return render_template('auth/modular_auth_reset_password.html', token=token)

# Import KYC related modules - TEMPORARILY DISABLED
# from .plaid_service import plaid_kyc_service
# from .kyc_models import PlaidKYCVerification, KYCAuditLog, KYCStatus
from flask import jsonify

# PLAID KYC ROUTES TEMPORARILY DISABLED
# All Plaid KYC verification routes have been temporarily disabled
# to resolve authentication service errors. Routes include:
# - /kyc/start (POST) - Start verification process
# - /kyc/create (POST) - Create verification 
# - /kyc/status/<verification_id> (GET) - Get status
# - /kyc/webhook (POST) - Handle webhooks
# - /kyc/dashboard (GET) - User dashboard
# 
# These routes will be re-enabled once Plaid API keys are properly configured
# and the KYC onboarding workflow is ready for production use.

# Placeholder route for future KYC verification endpoint
# This will handle the complete onboarding workflow once Plaid is configured
# @auth_bp.route('/kyc/create', methods=['POST'])
# @login_required  
# def create_kyc_verification():
#     """Create KYC verification for user onboarding"""
#     pass

# --- END OF AUTH MODULE ROUTES ---
