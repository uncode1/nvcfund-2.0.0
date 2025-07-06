"""
MFA Routes
NVC Banking Platform - Multi-Factor Authentication Web Routes

This module provides web endpoints for MFA functionality:
- MFA setup and configuration
- TOTP verification
- Backup code management
- MFA status and management
"""

from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from modules.mfa import mfa_bp
from modules.mfa.services import MFAService
from modules.core.security_enforcement import secure_banking_route, validate_input
import logging

logger = logging.getLogger(__name__)


@mfa_bp.route('/')
@login_required
@secure_banking_route(
    required_permissions=['mfa_access'],
    rate_limit={'requests_per_minute': 10},
    validation_rules={
        'required_fields': [],
        'optional_fields': []
    }
)
def mfa_dashboard():
    """MFA management dashboard"""
    try:
        # Get MFA status for current user
        mfa_status = MFAService.get_mfa_status(current_user.id)
        
        return render_template('mfa/dashboard.html', 
                             mfa_status=mfa_status)
        
    except Exception as e:
        logger.error(f"Error loading MFA dashboard for user {current_user.id}: {str(e)}")
        flash('Error loading MFA settings. Please try again.', 'error')
        return redirect(url_for('dashboard.dashboard_home'))


@mfa_bp.route('/setup')
@login_required
@secure_banking_route(
    required_permissions=['mfa_setup'],
    rate_limit={'requests_per_minute': 5},
    validation_rules={
        'required_fields': [],
        'optional_fields': []
    }
)
def setup_mfa():
    """Set up MFA for the user"""
    try:
        # Check if MFA is already enabled
        mfa_status = MFAService.get_mfa_status(current_user.id)
        if mfa_status['enabled']:
            flash('MFA is already enabled for your account.', 'info')
            return redirect(url_for('mfa.mfa_dashboard'))
        
        # Generate TOTP secret and QR code
        secret, qr_code_base64, error = MFAService.setup_totp(current_user.id)
        
        if error:
            flash(f'Error setting up MFA: {error}', 'error')
            return redirect(url_for('mfa.mfa_dashboard'))
        
        return render_template('mfa/setup_totp.html', 
                             secret=secret,
                             qr_code_base64=qr_code_base64)
        
    except Exception as e:
        logger.error(f"Error setting up MFA for user {current_user.id}: {str(e)}")
        flash('Error setting up MFA. Please try again.', 'error')
        return redirect(url_for('mfa.mfa_dashboard'))


@mfa_bp.route('/verify-setup', methods=['POST'])
@login_required
@secure_banking_route(
    required_permissions=['mfa_setup'],
    rate_limit={'requests_per_minute': 3},
    validation_rules={
        'required_fields': ['totp_code'],
        'optional_fields': []
    }
)
def verify_setup():
    """Verify TOTP code during setup"""
    try:
        totp_code = request.form.get('totp_code', '').strip()
        
        if not totp_code or len(totp_code) != 6 or not totp_code.isdigit():
            flash('Please enter a valid 6-digit code.', 'error')
            return redirect(url_for('mfa.setup_mfa'))
        
        # Verify the TOTP code
        success, result = MFAService.verify_totp_setup(current_user.id, totp_code)
        
        if success:
            # result contains backup codes
            backup_codes = result
            flash('MFA has been successfully enabled for your account!', 'success')
            return render_template('mfa/backup_codes.html', backup_codes=backup_codes)
        else:
            flash(f'Verification failed: {result}', 'error')
            return redirect(url_for('mfa.setup_mfa'))
        
    except Exception as e:
        logger.error(f"Error verifying MFA setup for user {current_user.id}: {str(e)}")
        flash('Error verifying MFA setup. Please try again.', 'error')
        return redirect(url_for('mfa.setup_mfa'))


@mfa_bp.route('/verify', methods=['GET', 'POST'])
def verify_mfa():
    """Verify MFA during login process"""
    try:
        # Check if user is in MFA verification state
        user_id = session.get('mfa_user_id')
        if not user_id:
            flash('Please log in first.', 'warning')
            return redirect(url_for('auth.login'))
        
        if request.method == 'GET':
            return render_template('mfa/verify.html')
        
        # POST request - verify the code
        totp_code = request.form.get('totp_code', '').strip()
        backup_code = request.form.get('backup_code', '').strip()
        
        if totp_code:
            # Verify TOTP code
            if len(totp_code) != 6 or not totp_code.isdigit():
                flash('Please enter a valid 6-digit code.', 'error')
                return render_template('mfa/verify.html')
            
            success, message = MFAService.verify_totp_login(user_id, totp_code)
            
        elif backup_code:
            # Verify backup code
            if len(backup_code) != 8 or not backup_code.isalnum():
                flash('Please enter a valid 8-character backup code.', 'error')
                return render_template('mfa/verify.html')
            
            success, message = MFAService.verify_backup_code(user_id, backup_code)
            
        else:
            flash('Please enter either a verification code or backup code.', 'error')
            return render_template('mfa/verify.html')
        
        if success:
            # Clear MFA session data
            session.pop('mfa_user_id', None)
            
            # Complete the login process
            from flask_login import login_user
            from modules.auth.models import User
            user = User.query.get(user_id)
            if user:
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard.dashboard_home'))
            else:
                flash('User not found. Please try logging in again.', 'error')
                return redirect(url_for('auth.login'))
        else:
            flash(f'Verification failed: {message}', 'error')
            return render_template('mfa/verify.html')
        
    except Exception as e:
        logger.error(f"Error during MFA verification: {str(e)}")
        flash('Error during verification. Please try again.', 'error')
        return render_template('mfa/verify.html')


@mfa_bp.route('/disable', methods=['POST'])
@login_required
@secure_banking_route(
    required_permissions=['mfa_management'],
    rate_limit={'requests_per_minute': 2},
    validation_rules={
        'required_fields': ['password'],
        'optional_fields': []
    }
)
def disable_mfa():
    """Disable MFA for the user (requires password confirmation)"""
    try:
        password = request.form.get('password', '')
        
        # Verify password before disabling MFA
        if not current_user.check_password(password):
            flash('Invalid password. MFA was not disabled.', 'error')
            return redirect(url_for('mfa.mfa_dashboard'))
        
        # Disable MFA
        success, message = MFAService.disable_mfa(current_user.id)
        
        if success:
            flash('MFA has been disabled for your account.', 'success')
        else:
            flash(f'Error disabling MFA: {message}', 'error')
        
        return redirect(url_for('mfa.mfa_dashboard'))
        
    except Exception as e:
        logger.error(f"Error disabling MFA for user {current_user.id}: {str(e)}")
        flash('Error disabling MFA. Please try again.', 'error')
        return redirect(url_for('mfa.mfa_dashboard'))


@mfa_bp.route('/regenerate-backup-codes', methods=['POST'])
@login_required
@secure_banking_route(
    required_permissions=['mfa_management'],
    rate_limit={'requests_per_minute': 1},
    validation_rules={
        'required_fields': [],
        'optional_fields': []
    }
)
def regenerate_backup_codes():
    """Regenerate backup codes for the user"""
    try:
        # Regenerate backup codes
        backup_codes, message = MFAService.regenerate_backup_codes(current_user.id)
        
        if backup_codes:
            flash('New backup codes have been generated.', 'success')
            return render_template('mfa/backup_codes.html', backup_codes=backup_codes)
        else:
            flash(f'Error regenerating backup codes: {message}', 'error')
            return redirect(url_for('mfa.mfa_dashboard'))
        
    except Exception as e:
        logger.error(f"Error regenerating backup codes for user {current_user.id}: {str(e)}")
        flash('Error regenerating backup codes. Please try again.', 'error')
        return redirect(url_for('mfa.mfa_dashboard'))


@mfa_bp.route('/status')
@login_required
@secure_banking_route(
    required_permissions=['mfa_access'],
    rate_limit={'requests_per_minute': 20},
    validation_rules={
        'required_fields': [],
        'optional_fields': []
    }
)
def mfa_status():
    """Get MFA status as JSON (for AJAX requests)"""
    try:
        status = MFAService.get_mfa_status(current_user.id)
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"Error getting MFA status for user {current_user.id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error getting MFA status'
        }), 500


@mfa_bp.route('/health')

@mfa_bp.route('/settings')

@mfa_bp.route('/activity')
@login_required
def activity_log():
    """MFA activity log"""
    try:
        return render_template('activity_log.html',
                             user=current_user,
                             page_title='MFA activity log')
    except Exception as e:
        error_service.log_error("ACTIVITY_LOG_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('mfa.main_dashboard'))
@login_required
def mfa_settings():
    """MFA settings management"""
    try:
        return render_template('mfa/settings.html',
                             user=current_user,
                             page_title='MFA settings management')
    except Exception as e:
        error_service.log_error("MFA_SETTINGS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('mfa.main_dashboard'))
def health_check():
    """MFA module health check"""
    try:
        return jsonify({
            'status': 'healthy',
            'app_module': 'mfa',
            'features': {
                'totp_authentication': True,
                'backup_codes': True,
                'qr_code_generation': True,
                'audit_logging': True
            }
        })
        
    except Exception as e:
        logger.error(f"MFA health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'app_module': 'mfa',
            'error': str(e)
        }), 500


# Error handlers for MFA module
@mfa_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors within MFA module"""
    return render_template('mfa/error.html', 
                         error_code=404,
                         error_message="MFA page not found"), 404


@mfa_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors within MFA module"""
    logger.error(f"MFA module internal error: {str(error)}")
    return render_template('mfa/error.html',
                         error_code=500,
                         error_message="Internal server error in MFA module"), 500