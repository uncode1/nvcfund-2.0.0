"""
Investment Services Routes
Enterprise-grade modular routing system
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from modules.utils.services import ErrorLoggerService

# Create module blueprint
investments_bp = Blueprint('investments', __name__, 
                            template_folder='templates',
                            static_folder='static',
                            url_prefix='/investments')

# Initialize services
error_service = ErrorLoggerService()

@investments_bp.route('/')
@login_required
def main_dashboard():
    """Investment Services main dashboard"""
    try:
        return render_template('investments/investments_dashboard.html',
                             user=current_user,
                             page_title='Investment Services Dashboard')
    except Exception as e:
        error_service.log_error("DASHBOARD_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.main_dashboard'))

@investments_bp.route('/overview')
@login_required  
def overview():
    """Investment Services overview page"""
    try:
        return render_template('investments/investments_overview.html',
                             user=current_user,
                             page_title='Investment Services Overview')
    except Exception as e:
        error_service.log_error("OVERVIEW_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')  
        return redirect(url_for('investments.main_dashboard'))

@investments_bp.route('/portfolio')
@login_required
def portfolio():
    """Investment portfolio overview"""
    try:
        return render_template('investments/portfolio_management.html',
                             user=current_user,
                             page_title='Portfolio Management')
    except Exception as e:
        error_service.log_error("PORTFOLIO_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('investments.main_dashboard'))

@investments_bp.route('/portfolio-management')
@investments_bp.route('/portfolio')
@login_required  
def portfolio_management():
    """Comprehensive portfolio management and analysis dashboard"""
    try:
        # Enhanced portfolio data with tools and analytics
        portfolio_data = {
            'total_value': 125000.00,
            'daily_change': 2.45,
            'daily_change_percent': 1.98,
            'total_return': 18500.00,
            'total_return_percent': 17.35,
            'holdings': [
                {'symbol': 'NVCT', 'name': 'NVC Token', 'value': 50000, 'change': 5.2, 'allocation': 40, 'shares': 1000, 'avg_cost': 45.00},
                {'symbol': 'AAPL', 'name': 'Apple Inc.', 'value': 25000, 'change': 1.8, 'allocation': 20, 'shares': 150, 'avg_cost': 160.00},
                {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'value': 20000, 'change': -0.5, 'allocation': 16, 'shares': 50, 'avg_cost': 380.00},
                {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'value': 15000, 'change': 2.1, 'allocation': 12, 'shares': 10, 'avg_cost': 1400.00},
                {'symbol': 'BTC', 'name': 'Bitcoin', 'value': 10000, 'change': 3.7, 'allocation': 8, 'shares': 0.25, 'avg_cost': 38000.00},
                {'symbol': 'ETH', 'name': 'Ethereum', 'value': 5000, 'change': 1.2, 'allocation': 4, 'shares': 2.5, 'avg_cost': 1900.00}
            ],
            'risk_metrics': {
                'beta': 1.15,
                'sharpe_ratio': 1.42,
                'volatility': 18.5,
                'max_drawdown': -12.3
            },
            'performance': {
                '1d': 2.45,
                '1w': 5.8,
                '1m': 12.4,
                '3m': 18.7,
                'ytd': 24.3,
                '1y': 17.35
            }
        }
        
        return render_template('investments/portfolio_management.html',
                             user=current_user,
                             portfolio=portfolio_data,
                             page_title='Portfolio Management')
    except Exception as e:
        error_service.log_error(f"Portfolio management error: {str(e)}", current_user.id)
        flash('Unable to load portfolio management. Please try again.', 'error')
        return redirect(url_for('investments.main_dashboard'))

@investments_bp.route('/settings')
@login_required
def settings():
    """Investment Services settings page"""
    try:
        return render_template('investments/investments_settings.html',
                             user=current_user,
                             page_title='Investment Services Settings')
    except Exception as e:
        error_service.log_error("SETTINGS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('investments.main_dashboard'))

# Module health check
@investments_bp.route('/api/health')
def health_check():
    """Investment Services health check"""
    return jsonify({
        "status": "healthy",
        "app_module": "Investment Services",
        "version": "1.0.0",
        "routes_active": 19
    })
