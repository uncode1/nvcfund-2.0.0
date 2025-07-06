"""
User Management Module - Routes
NVC Banking Platform - User Profile and Activity Management

Features:
- Profile management and editing
- Activity monitoring and logging
- User settings and preferences
- Account security management
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from core.extensions import db
from core.security_enforcement import secure_banking_route, admin_required
from core.utils.logger import BankingLogger

# Initialize module components
user_management_bp = Blueprint('user_management', __name__, url_prefix='/user-management', template_folder='templates')
logger = BankingLogger('user_management')

@user_management_bp.route('/')
@login_required
def user_dashboard():
    """User management dashboard"""
    try:
        return render_template('user_management/user_dashboard.html',
                             user=current_user,
                             page_title='User Dashboard')
    except Exception as e:
        logger.error(f"Error loading user dashboard: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.dashboard'))

@user_management_bp.route('/profile')
@login_required
@secure_banking_route(
    required_permissions=['profile_management'],
    rate_limit=10,
    validation_rules={
        'required_fields': [],
        'optional_fields': ['first_name', 'last_name', 'email', 'phone']
    }
)
def profile_management():
    """Profile management interface"""
    try:
        return render_template('user_management/profile_management.html',
                             user=current_user,
                             page_title='Profile Management')
    except Exception as e:
        logger.error(f"Error loading profile management for user {current_user.id}: {str(e)}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('user_management.user_dashboard'))

@user_management_bp.route('/activity')
@login_required
@secure_banking_route(
    required_permissions=['activity_monitoring'],
    rate_limit=10,
    validation_rules={
        'required_fields': [],
        'optional_fields': ['page', 'filter_type', 'date_range']
    }
)
def activity_monitoring():
    """Activity monitoring interface"""
    try:
        page = request.args.get('page', 1, type=int)
        filter_type = request.args.get('filter_type', 'all')
        
        return render_template('activity_monitoring.html',
                             user=current_user,
                             page_title='Activity Monitoring',
                             current_page=page,
                             filter_type=filter_type)
    except Exception as e:
        logger.error(f"Error loading activity monitoring for user {current_user.id}: {str(e)}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('user_management.user_dashboard'))

@user_management_bp.route('/settings')
@login_required
@secure_banking_route(
    required_permissions=['user_settings'],
    rate_limit=5,
    validation_rules={
        'required_fields': [],
        'optional_fields': ['notification_preferences', 'security_settings', 'privacy_controls']
    }
)
def user_settings():
    """User settings management"""
    try:
        return render_template('user_settings.html',
                             user=current_user,
                             page_title='User Settings')
    except Exception as e:
        logger.error(f"Error loading user settings for user {current_user.id}: {str(e)}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('user_management.user_dashboard'))

@user_management_bp.route('/api/health')
def health_check():
    """User management module health check"""
    return jsonify({
        'status': 'healthy',
        'app_module': 'user_management',
        'timestamp': datetime.utcnow().isoformat()
    })