"""
Accounts Management Routes
Enterprise-grade modular routing system
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from modules.utils.services import ErrorLoggerService

# Create module blueprint
accounts_bp = Blueprint('accounts', __name__, 
                            template_folder='templates',
                            static_folder='static',
                            url_prefix='/accounts')

# Initialize services
error_service = ErrorLoggerService()

@accounts_bp.route('/')
@login_required
def main_dashboard():
    """Accounts Management main dashboard"""
    try:
        return render_template('accounts/accounts_dashboard.html',
                             user=current_user,
                             page_title='Accounts Management Dashboard')
    except Exception as e:
        error_service.log_error("DASHBOARD_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.main_dashboard'))

@accounts_bp.route('/dashboard')
@login_required
def dashboard():
    """Accounts Management dashboard (alias for main)"""
    try:
        return render_template('accounts/accounts_dashboard.html',
                             user=current_user,
                             page_title='Accounts Management Dashboard')
    except Exception as e:
        error_service.log_error("DASHBOARD_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.main_dashboard'))

@accounts_bp.route('/overview')
@login_required  
def overview():
    """Accounts Management overview page"""
    try:
        # Get account data for the overview
        from modules.banking.models import BankAccount
        from modules.core.extensions import db
        
        # Sample account data for demonstration
        sample_accounts = [
            {
                'id': 1,
                'account_number': '1001234567',
                'account_name': 'John Doe - Checking',
                'account_type': 'Checking',
                'current_balance': 15847.52,
                'status': 'Active',
                'opened_date': '2024-01-15'
            },
            {
                'id': 2, 
                'account_number': '2001234568',
                'account_name': 'Jane Smith - Savings',
                'account_type': 'Savings',
                'current_balance': 85200.75,
                'status': 'Active',
                'opened_date': '2024-02-20'
            },
            {
                'id': 3,
                'account_number': '3001234569', 
                'account_name': 'ABC Corp - Business',
                'account_type': 'Business',
                'current_balance': 450000.00,
                'status': 'Active',
                'opened_date': '2024-03-10'
            },
            {
                'id': 4,
                'account_number': '4001234570',
                'account_name': 'Investment Portfolio',
                'account_type': 'Investment',
                'current_balance': 125000.00,
                'status': 'Active', 
                'opened_date': '2024-04-05'
            }
        ]
        
        # Account summary statistics
        total_accounts = len(sample_accounts)
        total_balance = sum(acc['current_balance'] for acc in sample_accounts)
        active_accounts = len([acc for acc in sample_accounts if acc['status'] == 'Active'])
        
        account_stats = {
            'total_accounts': total_accounts,
            'total_balance': total_balance,
            'active_accounts': active_accounts,
            'average_balance': total_balance / total_accounts if total_accounts > 0 else 0
        }
        
        return render_template('accounts/account_overview.html',
                             user=current_user,
                             accounts=sample_accounts,
                             account_stats=account_stats,
                             page_title='Account Overview')
    except Exception as e:
        error_service.log_error("OVERVIEW_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')  
        return redirect(url_for('accounts.main_dashboard'))

@accounts_bp.route('/settings')
@login_required
def settings():
    """Accounts Management settings page"""
    try:
        return render_template('accounts/accounts_settings.html',
                             user=current_user,
                             page_title='Accounts Management Settings')
    except Exception as e:
        error_service.log_error("SETTINGS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('accounts.main_dashboard'))

@accounts_bp.route('/analytics')
@login_required
def account_analytics():
    """Account analytics dashboard"""
    try:
        return render_template('accounts/account_analytics.html',
                             user=current_user,
                             page_title='Account Analytics')
    except Exception as e:
        error_service.log_error("ANALYTICS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('accounts.main_dashboard'))

@accounts_bp.route('/security')
@login_required
def account_security():
    """Account security management"""
    try:
        return render_template('accounts/account_security.html',
                             user=current_user,
                             page_title='Account Security')
    except Exception as e:
        error_service.log_error("SECURITY_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('accounts.main_dashboard'))

# Module health check
@accounts_bp.route('/api/health')
def health_check():
    """Accounts Management health check"""
    return jsonify({
        "status": "healthy",
        "app_module": "Accounts Management",
        "version": "1.0.0",
        "routes_active": 15
    })
