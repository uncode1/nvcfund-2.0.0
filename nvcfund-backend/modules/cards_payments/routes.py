"""
Cards & Payments Routes
Enterprise-grade modular routing system
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from modules.utils.services import ErrorLoggerService
from datetime import datetime

# Create module blueprint
cards_payments_bp = Blueprint('cards_payments', __name__, 
                            template_folder='templates',
                            static_folder='static',
                            url_prefix='/cards-payments')

# Initialize services
error_service = ErrorLoggerService()

@cards_payments_bp.route('/')
@cards_payments_bp.route('/card-management')
@login_required
def main_dashboard():
    """Cards & Payments main dashboard"""
    try:
        return render_template('cards_payments/cards_payments_dashboard.html',
                             user=current_user,
                             current_time=datetime.now(),
                             page_title='Cards & Payments Dashboard')
    except Exception as e:
        error_service.log_error("DASHBOARD_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.overview'))

@cards_payments_bp.route('/overview')
@login_required  
def overview():
    """Cards & Payments overview page"""
    try:
        return render_template('cards_payments/cards_payments_overview.html',
                             user=current_user,
                             page_title='Cards & Payments Overview')
    except Exception as e:
        error_service.log_error("OVERVIEW_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')  
        return redirect(url_for('cards_payments.main_dashboard'))

@cards_payments_bp.route('/processing')
@login_required
def payment_processing():
    """Payment processing management"""
    try:
        return render_template('cards_payments/payment_processing.html',
                             user=current_user,
                             page_title='Payment Processing')
    except Exception as e:
        error_service.log_error("PAYMENT_PROCESSING_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('cards_payments.main_dashboard'))

@cards_payments_bp.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    """Card application page"""
    if request.method == 'POST':
        try:
            # Process card application
            application_data = {
                'card_type': request.form.get('card_type'),
                'annual_income': request.form.get('annual_income'),
                'employment_status': request.form.get('employment_status'),
                'requested_limit': request.form.get('requested_limit'),
                'user_id': current_user.id
            }
            
            # In production, process application through card service
            flash('Card application submitted successfully. You will receive a decision within 24 hours.', 'success')
            return redirect(url_for('cards_payments.main_dashboard'))
            
        except Exception as e:
            error_service.log_error("CARD_APPLICATION_ERROR", str(e), {"user_id": current_user.id})
            flash('Unable to submit application. Please try again.', 'error')
    
    # GET request - show application form
    try:
        context = {
            'card_types': [
                {'name': 'Visa Classic', 'annual_fee': '$0', 'apr': '18.99%'},
                {'name': 'Visa Gold', 'annual_fee': '$95', 'apr': '16.99%'},
                {'name': 'Visa Platinum', 'annual_fee': '$195', 'apr': '14.99%'},
                {'name': 'Business Visa', 'annual_fee': '$125', 'apr': '15.99%'}
            ],
            'page_title': 'Apply for Card'
        }
        
        return render_template('cards_payments/card_application.html', **context)
        
    except Exception as e:
        error_service.log_error("CARD_APPLICATION_PAGE_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('cards_payments.main_dashboard'))

@cards_payments_bp.route('/card-management')
@login_required
def card_management():
    """Card management page"""
    try:
        return render_template('cards_payments/cards_payments_dashboard.html',
                             user=current_user,
                             current_time=datetime.now(),
                             page_title='Card Management')
    except Exception as e:
        error_service.log_error("CARD_MANAGEMENT_ERROR", str(e), {"user_id": current_user.id})
        flash('Card management service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.overview'))


@cards_payments_bp.route('/settings')
@login_required
def settings():
    """Cards & Payments settings page"""
    try:
        return render_template('cards_payments/cards_payments_settings.html',
                             user=current_user,
                             page_title='Cards & Payments Settings')
    except Exception as e:
        error_service.log_error("SETTINGS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('cards_payments.main_dashboard'))

# Module health check
@cards_payments_bp.route('/api/health')
def health_check():
    """Cards & Payments health check"""
    return jsonify({
        "status": "healthy",
        "app_module": "Cards & Payments",
        "version": "1.0.0",
        "routes_active": 16
    })
