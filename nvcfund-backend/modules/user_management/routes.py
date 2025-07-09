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

from modules.core.extensions import db
from modules.core.security_enforcement import secure_banking_route, admin_required
import logging

# Initialize module components with hyphenated URL for professional banking appearance
user_management_bp = Blueprint('user_management', __name__, 
                              template_folder='templates',
                              url_prefix='/user-management')

# Create legacy redirect blueprint for underscore URL
user_management_legacy_bp = Blueprint('user_management_legacy', __name__, 
                              template_folder='templates',
                              url_prefix='/user_management')

# Create legacy redirect blueprint for hyphenated URL  
user_management_hyphen_bp = Blueprint('user_management_hyphen', __name__, 
                              template_folder='templates',
                              url_prefix='/user-management')
logger = logging.getLogger(__name__)

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

@user_management_bp.route('/admin')
@login_required
@admin_required
def admin_user_management():
    """Super Admin user management dashboard with role navigation"""
    try:
        from modules.auth.models import User
        
        # Get all users with their roles
        users = db.session.query(User).all()
        
        # Organize users by role
        users_by_role = {}
        for user in users:
            role = user.role or 'standard_user'
            if role not in users_by_role:
                users_by_role[role] = []
            users_by_role[role].append({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role': user.role,
                'last_login': user.last_login,
                'created_at': user.created_at,
                'is_active': user.is_active,
                'department': getattr(user, 'department', 'General'),
                'phone': getattr(user, 'phone', 'Not provided')
            })
        
        # Role dashboard mappings
        role_dashboards = {
            'super_admin': {'route': 'dashboard.dashboard_home', 'name': 'Super Admin Dashboard'},
            'admin': {'route': 'admin_management.admin_dashboard', 'name': 'Admin Dashboard'},
            'treasury_officer': {'route': 'treasury.treasury_dashboard', 'name': 'Treasury Dashboard'},
            'compliance_officer': {'route': 'compliance.overview', 'name': 'Compliance Dashboard'},
            'branch_manager': {'route': 'admin_management.branch_management', 'name': 'Branch Manager Dashboard'},
            'customer_service': {'route': 'dashboard.dashboard_home', 'name': 'Customer Service Dashboard'},
            'risk_manager': {'route': 'compliance.overview', 'name': 'Risk Management Dashboard'},
            'sovereign_banker': {'route': 'sovereign.sovereign_dashboard', 'name': 'Sovereign Banking Dashboard'},
            'standard_user': {'route': 'dashboard.dashboard_home', 'name': 'Customer Dashboard'},
            'business_user': {'route': 'dashboard.dashboard_home', 'name': 'Business Customer Dashboard'}
        }
        
        # User statistics
        total_users = len(users)
        active_users = len([u for u in users if u.is_active])
        roles_count = len(users_by_role)
        
        return render_template('user_management/admin_user_management.html',
                             users_by_role=users_by_role,
                             role_dashboards=role_dashboards,
                             total_users=total_users,
                             active_users=active_users,
                             roles_count=roles_count,
                             page_title='Super Admin - User Management')
    except Exception as e:
        logger.error(f"Error loading admin user management: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.dashboard'))

@user_management_bp.route('/impersonate/<int:user_id>')
@login_required
@admin_required
def impersonate_user(user_id):
    """Allow super admin to experience user's role dashboard"""
    try:
        from modules.auth.models import User
        from flask_login import login_user
        
        # Get the target user
        target_user = User.query.get_or_404(user_id)
        
        # Store current super admin info in session for restoration
        from flask import session
        session['original_user_id'] = current_user.id
        session['original_user_role'] = current_user.role
        session['impersonating'] = True
        session['impersonated_user_id'] = user_id
        session['impersonated_user_role'] = target_user.role
        
        logger.info(f"Super admin {current_user.username} impersonating user {target_user.username} (Role: {target_user.role})")
        
        # Redirect to appropriate dashboard based on role
        role_routes = {
            'super_admin': 'dashboard.dashboard_home',
            'admin': 'admin_management.admin_dashboard', 
            'treasury_officer': 'treasury.treasury_dashboard',
            'compliance_officer': 'compliance.overview',
            'branch_manager': 'admin_management.branch_management',
            'customer_service': 'dashboard.dashboard_home',
            'risk_manager': 'compliance.overview',
            'sovereign_banker': 'sovereign.sovereign_dashboard',
            'standard_user': 'dashboard.dashboard_home',
            'business_user': 'dashboard.dashboard_home'
        }
        
        route = role_routes.get(target_user.role, 'dashboard.dashboard_home')
        flash(f'Now experiencing {target_user.first_name} {target_user.last_name}\'s dashboard ({target_user.role})', 'info')
        
        return redirect(url_for(route))
        
    except Exception as e:
        logger.error(f"Error impersonating user {user_id}: {e}")
        flash('Unable to access user dashboard', 'error')
        return redirect(url_for('user_management.admin_user_management'))

@user_management_bp.route('/stop-impersonation')
@login_required
def stop_impersonation():
    """Stop impersonation and return to super admin dashboard"""
    try:
        from flask import session
        
        if 'impersonating' in session:
            original_user_id = session.pop('original_user_id', None)
            session.pop('original_user_role', None)
            session.pop('impersonating', None)
            session.pop('impersonated_user_id', None)
            session.pop('impersonated_user_role', None)
            
            logger.info(f"Stopped impersonation, returning to super admin dashboard")
            flash('Returned to Super Admin view', 'success')
        
        return redirect(url_for('user_management.admin_user_management'))
        
    except Exception as e:
        logger.error(f"Error stopping impersonation: {e}")
        flash('Error returning to admin view', 'error')
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

@user_management_bp.route('/api/user/<int:user_id>')
@login_required
@admin_required
def get_user_details(user_id):
    """Get detailed user information for admin"""
    try:
        from modules.auth.models import User
        
        user = User.query.get_or_404(user_id)
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': user.role,
            'department': getattr(user, 'department', 'General'),
            'phone': getattr(user, 'phone', 'Not provided'),
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
        
        return jsonify(user_data)
        
    except Exception as e:
        logger.error(f"Error getting user details for user {user_id}: {e}")
        return jsonify({'error': 'Unable to load user details'}), 500

@user_management_bp.route('/api/health')
def health_check():
    """User management module health check"""
    return jsonify({
        'status': 'healthy',
        'app_module': 'user_management',
        'timestamp': datetime.utcnow().isoformat()
    })