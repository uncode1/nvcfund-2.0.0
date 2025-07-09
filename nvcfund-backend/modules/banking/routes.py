"""
Banking Module Routes - Comprehensive Banking Operations
Self-contained banking routes with account management, transfers, cards, and payments
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session, make_response
from flask_login import login_required, current_user
from flask_wtf.csrf import generate_csrf
from datetime import datetime
import logging
import os
from decimal import Decimal

from .services import BankingService
from modules.services.integrations.payment_gateways.services import PaymentGatewayService
from modules.utils.services import ErrorLoggerService
from modules.core.form_decorators import banking_form, process_form, require_post_data
from modules.core.form_processor import form_processor



# Initialize logging and services
logger = logging.getLogger(__name__)
banking_service = BankingService()
gateway_service = PaymentGatewayService()
error_service = ErrorLoggerService()

# Create Banking Blueprint
banking_bp = Blueprint('banking', __name__, 
                      template_folder='templates',
                      static_folder='static',
                      static_url_path='/banking/static',
                      url_prefix='/banking')

# Endpoint to log user onclick actions for debugging
@banking_bp.route('/log-action', methods=['POST'])
@login_required
def log_user_action():
    """Log user onclick actions for debugging"""
    try:
        data = request.get_json() or {}
        action = data.get('action', 'unknown')
        element = data.get('element', 'unknown')
        target_url = data.get('targetUrl', 'unknown')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Enhanced logging with clear action details
        logger.info(f"🎯 USER ONCLICK ACTION: {action} | Element: {element} | Target: {target_url} | User: {current_user.username}")
        print(f"🎯 USER ONCLICK ACTION: {action} | Element: {element} | Target: {target_url} | User: {current_user.username}")
        
        return jsonify({'status': 'logged', 'action': action})
    except Exception as e:
        logger.error(f"Failed to log user action: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Also add API route for consistency
@banking_bp.route('/api/log-user-action', methods=['POST'])
@login_required
def api_log_user_action():
    """API endpoint for logging user actions from JavaScript"""
    return log_user_action()

# Main Banking Dashboard
@banking_bp.route('/')
@banking_bp.route('/home')
@login_required
def banking_dashboard():
    """Banking dashboard with account overview"""
    try:
        user_accounts = banking_service.get_user_accounts(current_user.id)
        user_cards = banking_service.get_user_cards(current_user.id)
        recent_transfers = banking_service.get_transfer_history(current_user.id, limit=5)

        context = {
            'accounts': user_accounts,
            'cards': user_cards,
            'recent_transfers': recent_transfers,
            'total_balance': sum(acc['balance'] for acc in user_accounts),
            'active_cards': len([card for card in user_cards if card['status'] == 'Active'])
        }

        logger.info(f"Banking dashboard accessed by user {current_user.id}")
        return render_template('banking/modular_banking_dashboard.html', **context)

    except Exception as e:
        error_service.log_error(f"Banking dashboard error: {str(e)}", current_user.id)
        flash('Unable to load banking dashboard. Please try again.', 'error')
        return redirect(url_for('dashboard.main_dashboard'))

# Account Management Routes
@banking_bp.route('/accounts')
@login_required
def accounts():
    """Account management page"""
    try:
        user_accounts = banking_service.get_user_accounts(current_user.id)

        context = {
            'accounts': user_accounts,
            'page_title': 'Account Management'
        }

        return render_template('banking/modular_banking_accounts.html', **context)

    except Exception as e:
        error_service.log_error(f"Accounts page error: {str(e)}", current_user.id)
        flash('Unable to load accounts. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/accounts/create', methods=['GET', 'POST'])
@login_required
def create_account():
    """Create new account"""
    if request.method == 'POST':
        try:
            account_data = {
                'type': request.form.get('account_type'),
                'currency': request.form.get('currency', 'USD'),
                'branch': request.form.get('branch', 'Main Branch'),
                'initial_deposit': request.form.get('initial_deposit', '0.00')
            }

            result = banking_service.create_account(current_user.id, account_data)

            if result['success']:
                flash(f'Account application submitted successfully. Account Number: {result["account"]["account_number"]}', 'success')
                return redirect(url_for('banking.accounts'))
            else:
                flash(f'Account creation failed: {result["error"]}', 'error')

        except Exception as e:
            error_service.log_error(f"Account creation error: {str(e)}", current_user.id)
            flash('Unable to create account. Please try again.', 'error')

    # GET request - show account creation form
    context = {
        'account_types': ['Checking', 'Savings', 'Business', 'Investment'],
        'currencies': ['USD', 'EUR', 'GBP', 'CAD', 'AUD'],
        'page_title': 'Create New Account'
    }

    return render_template('banking/modular_banking_create_account.html', **context)

# Transfer Routes
@banking_bp.route('/transfer')
@login_required
def transfer():
    """Transfer page - redirect to transfers dashboard"""
    return redirect(url_for('banking.transfers'))

@banking_bp.route('/send-transfer')
@login_required
def send_transfer():
    """Send money transfer page - redirect to new transfer form"""
    return redirect(url_for('banking.new_transfer'))

@banking_bp.route('/transfers')
@login_required
def transfers():
    """Modern comprehensive transfer channels dashboard"""
    try:
        user_accounts = banking_service.get_user_accounts(current_user.id)

        # Redirect to account creation if no accounts
        if not user_accounts:
            flash('You need to create an account before making transfers.', 'info')
            return redirect(url_for('banking.create_account'))

        transfer_history = banking_service.get_transfer_history(current_user.id, limit=10)

        # Transfer channel metrics and options
        transfer_channels = [
            {
                'name': 'Internal Transfer',
                'description': 'Transfer between your NVC accounts',
                'icon': 'fas fa-arrows-alt-h',
                'color': 'primary',
                'speed': 'Instant',
                'cost': 'Free',
                'limit': '$50,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Instant processing', 'No fees', 'Real-time confirmation']
            },
            {
                'name': 'ACH Transfer',
                'description': 'US bank-to-bank transfers via ACH network',
                'icon': 'fas fa-university',
                'color': 'success',
                'speed': '1-3 business days',
                'cost': '$0.50',
                'limit': '$25,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Low cost', 'Secure', 'Batch processing']
            },
            {
                'name': 'Wire Transfer',
                'description': 'Fast domestic and international wire transfers',
                'icon': 'fas fa-bolt',
                'color': 'warning',
                'speed': '30 mins - 2 hours',
                'cost': '$15-35',
                'limit': '$1,000,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Same-day processing', 'High limits', 'Global reach']
            },
            {
                'name': 'SWIFT Transfer',
                'description': 'International transfers via SWIFT network',
                'icon': 'fas fa-globe',
                'color': 'info',
                'speed': '1-5 business days',
                'cost': '$25-50',
                'limit': '$500,000',
                'route': 'banking.swift_transfer',
                'available': True,
                'features': ['Worldwide coverage', 'Multi-currency', 'Tracking available']
            },
            {
                'name': 'Fedwire Transfer',
                'description': 'Federal Reserve real-time gross settlement',
                'icon': 'fas fa-university',
                'color': 'danger',
                'speed': 'Same day',
                'cost': '$30',
                'limit': '$10,000,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Same-day settlement', 'Large amounts', 'Federal Reserve network']
            },
            {
                'name': 'Blockchain Transfer',
                'description': 'Cryptocurrency and digital asset transfers',
                'icon': 'fab fa-bitcoin',
                'color': 'secondary',
                'speed': '10-60 minutes',
                'cost': '$2-10',
                'limit': '$100,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Decentralized', 'Programmable', 'Cross-border']
            },
            {
                'name': 'NVCT Transfer',
                'description': 'Transfer using NVCT stablecoin',
                'icon': 'fas fa-coins',
                'color': 'primary',
                'speed': 'Instant',
                'cost': '$0.25',
                'limit': '$250,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Stable value', 'Instant settlement', 'Low fees']
            },
            {
                'name': 'Mobile Transfer',
                'description': 'Send money to mobile wallets',
                'icon': 'fas fa-mobile-alt',
                'color': 'success',
                'speed': 'Instant',
                'cost': '$1-3',
                'limit': '$10,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Mobile-friendly', 'QR codes', 'Push notifications']
            },
            {
                'name': 'PayPal Transfer',
                'description': 'Global digital payments via PayPal network',
                'icon': 'fab fa-paypal',
                'color': 'primary',
                'speed': 'Instant',
                'cost': '2.9% + $0.30',
                'limit': '$60,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Global reach', 'Buyer protection', 'Mobile app']
            },
            {
                'name': 'Stripe Transfer',
                'description': 'Online payment processing and transfers',
                'icon': 'fab fa-stripe',
                'color': 'secondary',
                'speed': '2-7 business days',
                'cost': '2.9% + $0.30',
                'limit': '$2,000,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Developer-friendly', 'Global coverage', 'Real-time API']
            },
            {
                'name': 'Flutterwave',
                'description': 'African payment infrastructure and transfers',
                'icon': 'fas fa-credit-card',
                'color': 'warning',
                'speed': '1-3 business days',
                'cost': '1.4% + $0.25',
                'limit': '$500,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Pan-African', 'Multiple currencies', 'Mobile money']
            },
            {
                'name': 'Mojaloop',
                'description': 'Open-source financial inclusion platform',
                'icon': 'fas fa-handshake',
                'color': 'info',
                'speed': 'Real-time',
                'cost': '$0.05',
                'limit': '$25,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Financial inclusion', 'Interoperability', 'Low cost']
            }
        ]

        # Transfer statistics (updated for 12 channels)
        transfer_stats = {
            'total_volume': 3247692.50,
            'total_transfers': 22847,
            'success_rate': 99.8,
            'average_amount': 1547.25,
            'channels_active': len([c for c in transfer_channels if c['available']]),
            'daily_volume': 147832.50,
            'daily_transfers': 1124,
            'pending_transfers': 31
        }

        # Generate CSRF token safely
        try:
            csrf_token = generate_csrf()
        except Exception as csrf_error:
            logger.error(f"CSRF token generation error: {csrf_error}")
            csrf_token = ''
        
        context = {
            'accounts': user_accounts,
            'transfer_history': transfer_history,
            'transfer_channels': transfer_channels,
            'transfer_stats': transfer_stats,
            'page_title': 'Transfer Channels',
            'csrf_token': csrf_token
        }

        return render_template('banking/modern_transfer_dashboard.html', **context)

    except Exception as e:
        logger.error(f"Transfers page error: {str(e)} - User: {current_user.id}")
        print(f"DEBUG: Transfers page error - {str(e)} - Type: {type(e)}")
        import traceback
        traceback.print_exc()
        flash('Unable to load transfers. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/transfers/new', methods=['GET', 'POST'])
@login_required
@banking_form('transfer')
def new_transfer():
    """Create new money transfer"""
    if request.method == 'POST':
        try:
            transfer_data = {
                'from_account': request.form.get('from_account'),
                'to_account': request.form.get('to_account'),
                'amount': request.form.get('amount'),
                'currency': request.form.get('currency', 'USD'),
                'description': request.form.get('description', ''),
                'user_id': current_user.id
            }

            result = banking_service.process_transfer(current_user.id, transfer_data)

            if result['success']:
                flash(f'Transfer completed successfully. Transaction ID: {result["transaction_id"]}', 'success')
                return redirect(url_for('banking.transfers'))
            else:
                flash(f'Transfer failed: {result["error"]}', 'error')

        except Exception as e:
            error_service.log_error(f"Transfer processing error: {str(e)}", current_user.id)
            flash('Unable to process transfer. Please try again.', 'error')

    # GET request - show transfer form
    try:
        # Get the selected channel from URL parameter
        channel_param = request.args.get('channel', 'internal_transfer')
        
        # Channel parameter normalization (handle both hyphen and underscore formats)
        channel_mapping = {
            'swift-transfer': 'swift_transfer',
            'wire-transfer': 'wire_transfer', 
            'ach-transfer': 'ach_transfer',
            'paypal-transfer': 'paypal_transfer',
            'stripe-transfer': 'stripe_transfer',
            'blockchain-transfer': 'blockchain_transfer',
            'mobile-transfer': 'mobile_transfer',
            'nvct-stablecoin': 'nvct_stablecoin',
            'nvct-transfer': 'nvct_stablecoin',
            'internal-transfer': 'internal_transfer',
            'fedwire-transfer': 'fedwire'
        }
        
        channel = channel_mapping.get(channel_param, channel_param)
        
        # Log the channel resolution for troubleshooting (development only)
        is_development = os.environ.get('FLASK_ENV') == 'development' or os.environ.get('DEBUG_TRANSFERS') == 'true'
        if is_development:
            logger.info(f"🎯 CHANNEL RESOLUTION: {channel_param} -> {channel}")
            print(f"🎯 CHANNEL RESOLUTION: {channel_param} -> {channel}")
        
        user_accounts = banking_service.get_user_accounts(current_user.id)

        # Redirect to account creation if no accounts
        if not user_accounts:
            flash('You need to create an account before making transfers.', 'info')
            return redirect(url_for('banking.create_account'))

        # Channel-specific configurations
        channel_configs = {
            'internal_transfer': {
                'template': 'banking/transfers/internal_transfer.html',
                'title': 'Internal Transfer',
                'description': 'Transfer between your NVC accounts',
                'features': ['Instant processing', 'No fees', 'Real-time confirmation'],
                'limits': {'min': 1, 'max': 50000},
                'fee': 0,
                'processing_time': 'Instant'
            },
            'paypal_transfer': {
                'template': 'banking/transfers/paypal_transfer.html',
                'title': 'PayPal Transfer',
                'description': 'Send money via PayPal worldwide',
                'features': ['Global reach', 'Buyer protection', 'Instant to PayPal accounts'],
                'limits': {'min': 1, 'max': 10000},
                'fee': 2.9,
                'processing_time': 'Instant'
            },
            'stripe_transfer': {
                'template': 'banking/transfers/stripe_transfer.html',
                'title': 'Stripe Transfer',
                'description': 'Professional payment processing',
                'features': ['Secure processing', 'International support', 'Business-grade'],
                'limits': {'min': 1, 'max': 25000},
                'fee': 2.4,
                'processing_time': '2-7 business days'
            },
            'flutterwave': {
                'template': 'banking/transfers/flutterwave_transfer.html',
                'title': 'Flutterwave Transfer',
                'description': 'African payment gateway',
                'features': ['Pan-African coverage', 'Mobile money', 'Local currency support'],
                'limits': {'min': 1, 'max': 15000},
                'fee': 1.4,
                'processing_time': 'Instant to 24 hours'
            },
            'wire_transfer': {
                'template': 'banking/transfers/wire_transfer.html',
                'title': 'Wire Transfer',
                'description': 'Secure international wire transfers',
                'features': ['Global coverage', 'High security', 'Large amounts'],
                'limits': {'min': 100, 'max': 1000000},
                'fee': 25,
                'processing_time': '1-3 business days'
            },
            'swift_transfer': {
                'template': 'banking/transfers/wire_transfer.html',
                'title': 'SWIFT Transfer',
                'description': 'International transfers via SWIFT network',
                'features': ['Worldwide coverage', 'Multi-currency', 'Tracking available'],
                'limits': {'min': 100, 'max': 500000},
                'fee': 35,
                'processing_time': '1-5 business days'
            },
            'ach_transfer': {
                'template': 'banking/transfers/ach_transfer.html',
                'title': 'ACH Transfer',
                'description': 'US bank-to-bank transfers',
                'features': ['Low cost', 'Secure', 'US domestic only'],
                'limits': {'min': 1, 'max': 25000},
                'fee': 0.50,
                'processing_time': '1-3 business days'
            },
            'fedwire': {
                'template': 'banking/transfers/fedwire_transfer.html',
                'title': 'Fedwire Transfer',
                'description': 'Federal Reserve real-time gross settlement',
                'features': ['Same-day settlement', 'Large amounts', 'Federal Reserve network'],
                'limits': {'min': 1000, 'max': 10000000},
                'fee': 30,
                'processing_time': 'Same day'
            },
            'blockchain_transfer': {
                'template': 'banking/transfers/blockchain_transfer.html',
                'title': 'Blockchain Transfer',
                'description': 'Cryptocurrency and digital asset transfers',
                'features': ['Decentralized', 'Global reach', 'Smart contracts'],
                'limits': {'min': 1, 'max': 100000},
                'fee': 2.0,
                'processing_time': '5-30 minutes'
            },
            'mojaloop': {
                'template': 'banking/transfers/mojaloop_transfer.html',
                'title': 'Mojaloop Transfer',
                'description': 'Open-source financial inclusion platform',
                'features': ['Financial inclusion', 'Interoperability', 'Low cost'],
                'limits': {'min': 1, 'max': 25000},
                'fee': 0.05,
                'processing_time': 'Real-time'
            },
            'mobile_transfer': {
                'template': 'banking/transfers/mobile_transfer.html',
                'title': 'Mobile Transfer',
                'description': 'Mobile money and SMS-based transfers',
                'features': ['No internet required', 'SMS-based', 'Mobile wallet'],
                'limits': {'min': 1, 'max': 5000},
                'fee': 1.0,
                'processing_time': 'Instant'
            },
            'nvct_stablecoin': {
                'template': 'banking/transfers/nvct_stablecoin_transfer.html',
                'title': 'NVCT Stablecoin Transfer',
                'description': 'NVC token stablecoin transfers',
                'features': ['Stable value', 'Blockchain-based', 'Low volatility'],
                'limits': {'min': 1, 'max': 1000000},
                'fee': 0.25,
                'processing_time': '2-5 minutes'
            }
        }

        # Get configuration for selected channel
        config = channel_configs.get(channel, channel_configs['internal_transfer'])

        context = {
            'accounts': user_accounts,
            'currencies': ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'NVCT', 'BTC', 'ETH'],
            'channel': channel,
            'channel_config': config,
            'page_title': config['title']
        }

        # Add troubleshooting headers for better debugging
        response = make_response(render_template(config['template'], **context))
        response.headers['X-Served-Channel'] = channel
        response.headers['X-Template-Used'] = config['template']
        response.headers['X-Final-URL'] = f"/banking/transfers/new?channel={channel}"
        
        # Enhanced response logging with served details (development/verbose only)
        served_details = f"Template={config['template']}, Channel={channel}, Title={config['title']}"
        if is_development:
            logger.info(f"🎯 SERVING: {served_details}")
            logger.info(f"🎯 RESPONSE DETAILS: 200 OK | Served: {served_details} | URL: /banking/transfers/new?channel={channel}")
            print(f"🎯 SERVING: {served_details}")
            print(f"🎯 RESPONSE DETAILS: 200 OK | Served: {served_details} | URL: /banking/transfers/new?channel={channel}")
        else:
            # Production: minimal logging for troubleshooting
            logger.debug(f"Transfer channel served: {channel} -> {config['template']}")
        
        return response

    except Exception as e:
        error_service.log_error(f"New transfer page error: {str(e)}", current_user.id)
        flash('Unable to load transfer form. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/transfers/send', methods=['POST'])
@login_required
def process_send_transfer():
    """Process money transfer"""
    try:
        transfer_data = {
            'from_account': request.form.get('from_account'),
            'to_account': request.form.get('to_account'),
            'amount': request.form.get('amount'),
            'currency': request.form.get('currency', 'USD'),
            'description': request.form.get('description', ''),
            'user_id': current_user.id
        }

        # Validate transfer amount
        try:
            amount = Decimal(transfer_data['amount'])
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except (ValueError, TypeError):
            flash('Invalid transfer amount.', 'error')
            return redirect(url_for('banking.transfers'))

        result = banking_service.process_transfer(transfer_data)

        if result['success']:
            flash(f'Transfer initiated successfully. Reference: {result["transfer"]["transfer_id"]}', 'success')
        else:
            flash(f'Transfer failed: {result["error"]}', 'error')

    except Exception as e:
        error_service.log_error(f"Transfer processing error: {str(e)}", current_user.id)
        flash('Unable to process transfer. Please try again.', 'error')

    return redirect(url_for('banking.transfers'))

# Card Management Routes
@banking_bp.route('/cards')
@login_required
def cards():
    """Card management page"""
    try:
        user_cards = banking_service.get_user_cards(current_user.id)
        user_accounts = banking_service.get_user_accounts(current_user.id)

        context = {
            'cards': user_cards,
            'accounts': user_accounts,
            'page_title': 'Card Management'
        }

        return render_template('banking/modular_banking_cards.html', **context)

    except Exception as e:
        error_service.log_error(f"Cards page error: {str(e)}", current_user.id)
        flash('Unable to load cards. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/cards/apply', methods=['GET', 'POST'])
@login_required
def apply_card():
    """Card application"""
    if request.method == 'POST':
        try:
            card_data = {
                'card_type': request.form.get('card_type'),
                'network': request.form.get('network'),
                'linked_account': request.form.get('linked_account'),
                'express_delivery': request.form.get('express_delivery') == 'on'
            }

            result = banking_service.apply_for_card(current_user.id, card_data)

            if result['success']:
                flash(f'Card application submitted. Application ID: {result["application"]["application_id"]}', 'success')
                return redirect(url_for('banking.cards'))
            else:
                flash(f'Card application failed: {result["error"]}', 'error')

        except Exception as e:
            error_service.log_error(f"Card application error: {str(e)}", current_user.id)
            flash('Unable to submit card application. Please try again.', 'error')

    # GET request - show card application form
    user_accounts = banking_service.get_user_accounts(current_user.id)

    context = {
        'card_types': ['Debit', 'Credit', 'Prepaid'],
        'networks': ['Visa', 'Mastercard', 'American Express', 'Discover'],
        'accounts': user_accounts,
        'page_title': 'Apply for Card'
    }

    # Generate CSRF token properly
    from flask_wtf.csrf import generate_csrf
    context['csrf_token'] = generate_csrf()

    return render_template('banking/modular_banking_card_application.html', **context)

# Payment Routes
@banking_bp.route('/payments')
@login_required
def payments():
    """Payment management page"""
    try:
        payment_methods = banking_service.get_payment_methods(current_user.id)

        context = {
            'payment_methods': payment_methods,
            'page_title': 'Payment Management'
        }

        return render_template('banking/modular_banking_payments.html', **context)

    except Exception as e:
        error_service.log_error(f"Payments page error: {str(e)}", current_user.id)
        flash('Unable to load payments. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/payments/send', methods=['POST'])
@login_required
def send_payment():
    """Process payment"""
    try:
        payment_data = {
            'recipient': request.form.get('recipient'),
            'amount': request.form.get('amount'),
            'currency': request.form.get('currency', 'USD'),
            'payment_method': request.form.get('payment_method'),
            'description': request.form.get('description', ''),
            'user_id': current_user.id
        }

        result = banking_service.process_payment(payment_data)

        if result['success']:
            flash(f'Payment processed successfully. Reference: {result["payment"]["payment_id"]}', 'success')
        else:
            flash(f'Payment failed: {result["error"]}', 'error')

    except Exception as e:
        error_service.log_error(f"Payment processing error: {str(e)}", current_user.id)
        flash('Unable to process payment. Please try again.', 'error')

    return redirect(url_for('banking.payments'))

# Transfer History
@banking_bp.route('/transfer-history')
@banking_bp.route('/transaction_history')  # Add alias for legacy navigation links
@login_required
def transfer_history():
    """Transfer history page"""
    try:
        transfers = banking_service.get_transfer_history(current_user.id, limit=100)

        context = {
            'transfers': transfers,
            'page_title': 'Transfer History'
        }

        return render_template('banking/transfer_history.html', **context)

    except Exception as e:
        error_service.log_error(f"Transfer history error: {str(e)}", current_user.id)
        flash('Unable to load transfer history. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Transaction History
@banking_bp.route('/history')
@banking_bp.route('/transaction-history')  # Alias for convenience
@login_required
def transaction_history():
    """Complete transaction history"""
    try:
        transfers = banking_service.get_transfer_history(current_user.id, limit=100)

        context = {
            'transactions': transfers,
            'page_title': 'Transaction History'
        }

        return render_template('banking/modular_banking_history.html', **context)

    except Exception as e:
        error_service.log_error(f"Transaction history error: {str(e)}", current_user.id)
        flash('Unable to load transaction history. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Account Statements
@banking_bp.route('/statements')
@login_required
def statements():
    """Account statements page"""
    try:
        user_accounts = banking_service.get_user_accounts(current_user.id)

        context = {
            'accounts': user_accounts,
            'page_title': 'Account Statements'
        }

        return render_template('banking/modular_banking_statements.html', **context)

    except Exception as e:
        error_service.log_error(f"Statements page error: {str(e)}", current_user.id)
        flash('Unable to load statements. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/statements/generate', methods=['GET', 'POST'])
@login_required
def generate_statement():
    """Generate account statement"""
    try:
        if request.method == 'GET':
            # Show statement generation form
            accounts = banking_service.get_user_accounts(current_user.id)
            return render_template('banking/generate_statement.html', accounts=accounts)

        # POST request - process statement generation
        account_id = request.form.get('account_id')
        period = request.form.get('period', 'monthly')

        if not account_id:
            flash('Please select an account.', 'error')
            return redirect(url_for('banking.generate_statement'))

        result = banking_service.generate_statement(current_user.id, int(account_id), period)

        if result['success']:
            flash(f'Statement generated successfully. ID: {result["statement"]["statement_id"]}', 'success')
        else:
            flash(f'Statement generation failed: {result["error"]}', 'error')

    except Exception as e:
        error_service.log_error(f"Statement generation error: {str(e)}", current_user.id)
        flash('Unable to generate statement. Please try again.', 'error')

    return redirect(url_for('banking.statements'))

@banking_bp.route('/accounts/history')
@login_required
def history():
    """Transaction history page"""
    try:
        # Sample transaction data for display
        sample_transactions = [
            {
                'id': 1,
                'date': 'December 17, 2024',
                'time': '2:30 PM',
                'description': 'Transfer to Savings',
                'type': 'transfer',
                'amount': -500.00,
                'balance': 45280.25,
                'status': 'completed',
                'reference': 'TXN-001',
                'account_number': 'SAV-007-000001',
                'account_type': 'Checking'
            },
            {
                'id': 2,
                'date': 'December 15, 2024',
                'time': '10:15 AM',
                'description': 'Salary Deposit',
                'type': 'deposit',
                'amount': 3500.00,
                'balance': 45780.25,
                'status': 'completed',
                'reference': 'TXN-002',
                'account_number': 'SAV-007-000001',
                'account_type': 'Checking'
            }
        ]

        context = {
            'transactions': sample_transactions,
            'page_title': 'Transaction History'
        }

        logger.info(f"Transaction history accessed by user {current_user.id}")
        return render_template('banking/modular_banking_history.html', **context)

    except Exception as e:
        error_service.log_error(f"Transaction history error: {str(e)}", current_user.id)
        flash('Unable to load transaction history. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Duplicate create_account function removed - using main one at line 75

@banking_bp.route('/security')
@login_required
def security():
    """Banking security settings"""
    return render_template('banking/modular_banking_security.html', 
                         user=current_user, 
                         page_title='Security Settings')

# Duplicate send_transfer function removed - using main one at line 137

# Duplicate apply_card function removed - using main one at line 195

# Legacy Banking Operations Integration (Phase 3 Consolidation)

@banking_bp.route('/payment-history')
@login_required
def payment_history():
    """Payment history from legacy payment routes"""
    try:
        payments = banking_service.get_payment_history(current_user.id)

        logger.info(f"Payment history accessed by user {current_user.id}")
        return render_template('banking/legacy_payment_history.html', 
                             payments=payments, 
                             title="Payment History")
    except Exception as e:
        error_service.log_error(f"Payment history error: {str(e)}", current_user.id)
        flash('Unable to load payment history. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/make-payment', methods=['GET', 'POST'])
@login_required
def make_payment():
    """Make payment from legacy payment routes"""
    try:
        if request.method == 'POST':
            payment_data = {
                'user_id': current_user.id,
                'amount': request.form.get('amount'),
                'recipient': request.form.get('recipient'),
                'payment_method': request.form.get('payment_method'),
                'description': request.form.get('description', '')
            }

            result = banking_service.process_payment(payment_data)

            if result.get('success'):
                flash('Payment processed successfully.', 'success')
                logger.info(f"Payment processed by user {current_user.id}: {result['payment']['payment_id']}")
                return redirect(url_for('banking.payment_history'))
            else:
                flash(f'Payment failed: {result.get("error")}', 'error')

        # GET request - show payment form
        gateways = banking_service.get_payment_gateways(current_user.id)

        return render_template('banking/legacy_make_payment.html', 
                             gateways=gateways, 
                             title="Make Payment")
    except Exception as e:
        error_service.log_error(f"Make payment error: {str(e)}", current_user.id)
        flash('Unable to process payment. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Duplicate transaction_history function removed - using main one at line 280

@banking_bp.route('/transaction-details/<transaction_id>')
@login_required
def transaction_details(transaction_id):
    """Transaction details from legacy banking routes"""
    try:
        transaction = banking_service.get_transaction_details(current_user.id, transaction_id)

        if not transaction:
            flash('Transaction not found.', 'error')
            return redirect(url_for('banking.transaction_history'))

        logger.info(f"Transaction details accessed by user {current_user.id}: {transaction_id}")
        return render_template('banking/legacy_transaction_details.html', 
                             transaction=transaction, 
                             title="Transaction Details")
    except Exception as e:
        error_service.log_error(f"Transaction details error: {str(e)}", current_user.id)
        flash('Unable to load transaction details. Please try again.', 'error')
        return redirect(url_for('banking.transaction_history'))

@banking_bp.route('/account-statements')
@login_required
def account_statements():
    """Account statements from legacy banking routes"""
    try:
        accounts = banking_service.get_user_accounts(current_user.id)

        # Default to first account if available
        account_id = request.args.get('account_id')
        if not account_id and accounts:
            account_id = accounts[0]['id']

        statement = None
        if account_id:
            statement = banking_service.get_account_statements(current_user.id, int(account_id))

        logger.info(f"Account statements accessed by user {current_user.id}")
        return render_template('banking/legacy_account_statements.html', 
                             accounts=accounts, 
                             statement=statement, 
                             selected_account=account_id,
                             title="Account Statements")
    except Exception as e:
        error_service.log_error(f"Account statements error: {str(e)}", current_user.id)
        flash('Unable to load account statements. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/business-services')
@login_required
def business_services():
    """Business banking services from legacy business routes"""
    try:
        services = banking_service.get_business_banking_services(current_user.id)

        logger.info(f"Business services accessed by user {current_user.id}")
        return render_template('banking/legacy_business_services.html', 
                             services=services, 
                             title="Business Banking Services")
    except Exception as e:
        error_service.log_error(f"Business services error: {str(e)}", current_user.id)
        flash('Unable to load business services. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/international-transfers')
@login_required
def international_transfers():
    """International transfer options from legacy transfer routes"""
    try:
        options = banking_service.get_international_transfer_options(current_user.id)

        logger.info(f"International transfers accessed by user {current_user.id}")
        return render_template('banking/legacy_international_transfers.html', 
                             transfer_options=options, 
                             title="International Transfers")
    except Exception as e:
        error_service.log_error(f"International transfers error: {str(e)}", current_user.id)
        flash('Unable to load international transfer options. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Additional Missing Banking Routes for Navigation Dropdown

@banking_bp.route('/wire-transfers')
@login_required
def wire_transfers():
    """Wire transfer services"""
    try:
        wire_data = {
            'available_currencies': ['USD', 'EUR', 'GBP', 'JPY'],
            'processing_times': {'standard': '1-3 days', 'express': 'same day'},
            'fees': {'domestic': 15, 'international': 45}
        }

        return render_template('banking/wire_transfers.html', 
                             wire_data=wire_data,
                             page_title='Wire Transfers')
    except Exception as e:
        error_service.log_error(f"Wire transfers error: {str(e)}", current_user.id)
        flash('Unable to load wire transfers. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/bill-payment')
@banking_bp.route('/bill_payment')  # Add alias for legacy navigation links
@login_required
def bill_payment():
    """Enhanced bill payment services with comprehensive features"""
    try:
        # Get comprehensive bill payment data
        payment_history = banking_service.get_bill_payment_history(current_user.id)
        saved_payees = banking_service.get_saved_payees(current_user.id)

        bill_data = {
            'bill_categories': ['Utilities', 'Telecom', 'Insurance', 'Loans', 'Credit Cards'],
            'saved_payees': saved_payees,
            'payment_history': payment_history,
            'quick_pay_options': [
                {'name': 'Electric Company', 'category': 'Utilities', 'last_amount': '125.45'},
                {'name': 'Internet Provider', 'category': 'Telecom', 'last_amount': '89.99'},
                {'name': 'Auto Insurance', 'category': 'Insurance', 'last_amount': '234.67'}
            ],
            'monthly_stats': {
                'total_paid': sum([float(p.get('amount', 0)) for p in payment_history[:30]]),  
                'payments_count': len(payment_history),
                'avg_amount': sum([float(p.get('amount', 0)) for p in payment_history[:10]]) / max(len(payment_history[:10]), 1)
            }
        }

        # Generate CSRF token safely
        try:
            csrf_token = generate_csrf()
        except Exception as csrf_error:
            logger.error(f"CSRF token generation error: {csrf_error}")
            csrf_token = ''

        return render_template('banking/bill_payment.html', 
                             bill_data=bill_data,
                             page_title='Bill Payment',
                             csrf_token=csrf_token)
    except Exception as e:
        error_service.log_error(f"Bill payment error: {str(e)}", current_user.id)
        flash('Unable to load bill payment. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/process-bill-payment', methods=['POST'])
@login_required
def process_bill_payment():
    """Process bill payment"""
    try:
        payment_data = {
            'payee_name': request.form.get('payee_name'),
            'account_number': request.form.get('account_number'),
            'amount': float(request.form.get('amount', 0)),
            'category': request.form.get('category'),
            'due_date': request.form.get('due_date'),
            'memo': request.form.get('memo', '')
        }

        # Process the payment (this would integrate with actual payment processing)
        result = banking_service.process_bill_payment(current_user.id, payment_data)

        if result.get('success'):
            flash(f'Bill payment processed successfully. Reference: {result.get("reference_id")}', 'success')
        else:
            flash(f'Bill payment failed: {result.get("error", "Unknown error")}', 'error')

    except Exception as e:
        error_service.log_error(f"Bill payment processing error: {str(e)}", current_user.id)
        flash('Unable to process bill payment. Please try again.', 'error')

    return redirect(url_for('banking.bill_payment'))

@banking_bp.route('/schedule-bill-payment', methods=['POST'])
@login_required
def schedule_bill_payment():
    """Schedule a future bill payment"""
    try:
        payment_data = {
            'payee_name': request.form.get('payee_name'),
            'amount': float(request.form.get('amount', 0)),
            'category': request.form.get('category'),
            'scheduled_date': request.form.get('scheduled_date'),
            'frequency': request.form.get('frequency', 'once')
        }

        result = banking_service.schedule_bill_payment(current_user.id, payment_data)

        if result.get('success'):
            flash(f'Bill payment scheduled successfully. Schedule ID: {result.get("schedule_id")}', 'success')
        else:
            flash(f'Scheduling failed: {result.get("error", "Unknown error")}', 'error')

    except Exception as e:
        error_service.log_error(f"Bill payment scheduling error: {str(e)}", current_user.id)
        flash('Unable to schedule bill payment. Please try again.', 'error')

    return redirect(url_for('banking.bill_payment'))

@banking_bp.route('/saved-payees')
@login_required
def saved_payees():
    """View and manage saved payees"""
    try:
        payees = banking_service.get_saved_payees(current_user.id)
        
        return render_template('banking/saved_payees.html',
                             payees=payees,
                             page_title='Saved Payees')
    except Exception as e:
        error_service.log_error(f"Saved payees error: {str(e)}", current_user.id)
        flash('Unable to load saved payees. Please try again.', 'error')
        return redirect(url_for('banking.bill_payment'))

@banking_bp.route('/scheduled-payments')
@login_required
def scheduled_payments():
    """Scheduled payment management"""
    try:
        scheduled_data = {
            'upcoming_payments': [],
            'payment_templates': []
        }

        return render_template('banking/scheduled_payments.html', 
                             scheduled_data=scheduled_data,
                             page_title='Scheduled Payments')
    except Exception as e:
        error_service.log_error(f"Scheduled payments error: {str(e)}", current_user.id)
        flash('Unable to load scheduled payments. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/recurring-payments')
@login_required
def recurring_payments():
    """Recurring payment management"""
    try:
        recurring_data = {
            'active_subscriptions': [],
            'payment_schedules': []
        }

        return render_template('banking/recurring_payments.html', 
                             recurring_data=recurring_data,
                             page_title='Recurring Payments')
    except Exception as e:
        error_service.log_error(f"Recurring payments error: {str(e)}", current_user.id)
        flash('Unable to load recurring payments. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/notifications')
@login_required
def notifications():
    """Banking notifications"""
    try:
        notifications_data = {
            'unread_notifications': [],
            'notification_settings': {}
        }

        return render_template('banking/notifications.html', 
                             notifications_data=notifications_data,
                             page_title='Notifications')
    except Exception as e:
        error_service.log_error(f"Notifications error: {str(e)}", current_user.id)
        flash('Unable to load notifications. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/preferences')
@login_required
def preferences():
    """Banking preferences"""
    try:
        preferences_data = {
            'language': 'en',
            'currency': 'USD',
            'timezone': 'UTC'
        }

        return render_template('banking/preferences.html', 
                             preferences_data=preferences_data,
                             page_title='Preferences')
    except Exception as e:
        error_service.log_error(f"Preferences error: {str(e)}", current_user.id)
        flash('Unable to load preferences. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Transaction Statement Download
@banking_bp.route('/statements/transaction/<int:transaction_id>')
@login_required
def download_transaction_statement(transaction_id):
    """Download transaction statement/receipt as PDF"""
    try:
        from flask import make_response
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.colors import black, blue
        from reportlab.lib.units import inch
        from io import BytesIO

        # Get transaction details
        transaction = banking_service.get_transaction_details(current_user.id, transaction_id)

        if not transaction:
            flash('Transaction not found.', 'error')
            return redirect(url_for('banking.transaction_history'))

        # Create PDF in memory
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Header
        p.setFont("Helvetica-Bold", 18)
        p.setFillColor(blue)
        p.drawString(50, height - 50, "NVC BANKING PLATFORM")

        p.setFont("Helvetica-Bold", 14)
        p.setFillColor(black)
        p.drawString(50, height - 80, "Transaction Receipt")

        # Draw line
        p.line(50, height - 90, width - 50, height - 90)

        # Transaction details
        y_position = height - 130
        line_height = 25

        p.setFont("Helvetica", 12)

        details = [
            f"Transaction ID: {transaction_id}",
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Account: ****{str(transaction_id)[-4:]}",
            f"Type: Transfer",
            f"Amount: $500.00",
            f"Status: Completed",
            "",
            f"Reference: REF-{transaction_id}",
            f"Description: Monthly rent payment"
        ]
        y_position -= 15
        p.drawString(50, y_position, "Phone: (555) 123-4567")

        # Disclaimer
        y_position -= 30
        p.setFont("Helvetica-Oblique", 8)
        p.drawString(50, y_position, "This is a computer-generated receipt. No signature required.")

        # Save PDF
        p.showPage()
        p.save()

        # Get PDF data
        buffer.seek(0)
        pdf_data = buffer.getvalue()
        buffer.close()

        # Create response for download
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=transaction_{transaction_id}_receipt.pdf'

        logger.info(f"Transaction PDF statement downloaded by user {current_user.id}: {transaction_id}")
        return response

    except Exception as e:
        error_service.log_error(f"Transaction PDF statement download error: {str(e)}", current_user.id)
        flash('Unable to download transaction statement. Please try again.', 'error')
        return redirect(url_for('banking.transaction_history'))

# Drill-down routes for detailed views
@banking_bp.route('/accounts/detailed')
@login_required
def accounts_detailed():
    """Detailed accounts drill-down view"""

@banking_bp.route('/transfers/management')
@login_required
def transfers_management():
    """Transfer management drill-down view"""
    try:
        return render_template('banking/transfers_management.html',
                             user=current_user,
                             page_title='Transfer Management')
    except Exception as e:
        error_service.log_error("TRANSFERS_MANAGEMENT_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/cards/management')
@login_required
def cards_management():
    """Cards management drill-down view"""
    try:
        return render_template('banking/cards_management.html',
                             user=current_user,
                             page_title='Cards Management')
    except Exception as e:
        error_service.log_error("CARDS_MANAGEMENT_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/transactions-analysis')
@login_required
def transactions_analysis():
    """Transaction analysis page"""
    try:
        # Get user transaction analytics
        transactions = banking_service.get_transfer_history(current_user.id, limit=100)
        
        # Basic analytics for now
        analytics = {
            'total_transactions': len(transactions),
            'total_amount': sum(t.get('amount', 0) for t in transactions),
            'average_amount': sum(t.get('amount', 0) for t in transactions) / len(transactions) if transactions else 0,
            'monthly_trend': []  # Can be enhanced later
        }
        
        return render_template('banking/transaction_history.html',
                             transactions=transactions,
                             analytics=analytics,
                             user=current_user,
                             page_title='Transaction Analysis')
    except Exception as e:
        error_service.log_error("TRANSACTIONS_ANALYSIS_ERROR", str(e), {"user_id": current_user.id})
        flash('Unable to load transaction analysis', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Account Detail Routes
# Payment Gateway Integration Routes (now handled by payment_gateways module)

@banking_bp.route('/accounts/<account_id>')
@login_required
def account_details(account_id):
    """Individual account details view"""
    try:
        # Get account details for the specific account
        account_data = {
            'account_id': account_id,
            'account_type': 'Savings Account' if 'SAV' in account_id else 'Checking Account',
            'balance': 45750.00,
            'available_balance': 45750.00,
            'account_number': account_id,
            'routing_number': '123456789',
            'interest_rate': 2.5 if 'SAV' in account_id else 0.1,
            'opened_date': '2023-01-15',
            'status': 'Active'
        }

        # Get recent transactions for this account
        recent_transactions = [
            {
                'date': '2025-01-05',
                'description': 'Direct Deposit - Salary',
                'amount': 5500.00,
                'type': 'credit',
                'balance': 45750.00
            },
            {
                'date': '2025-01-04',
                'description': 'Online Transfer',
                'amount': -150.00,
                'type': 'debit',
                'balance': 40250.00
            },
            {
                'date': '2025-01-03',
                'description': 'ATM Withdrawal',
                'amount': -200.00,
                'type': 'debit',
                'balance': 40400.00
            }
        ]

        return render_template('banking/account_details.html',
                             account=account_data,
                             transactions=recent_transactions,
                             page_title=f'Account Details - {account_id}')

    except Exception as e:
        error_service.log_error(f"Account details error: {str(e)}", current_user.id)
        flash('Unable to load account details. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Duplicate create_account function removed - using main one at line 75

# Duplicate apply_card function removed - using main one at line 195

# Legacy Banking Operations Integration (Phase 3 Consolidation)

        flash('Unable to load transaction details. Please try again.', 'error')
        return redirect(url_for('banking.transaction_history'))

# Additional Missing Banking Routes for Navigation Dropdown

    try:
        # Get bill payment history for the current user
        payment_history = banking_service.get_bill_payment_history(current_user.id)

        bill_data = {
            'bill_categories': ['Utilities', 'Telecom', 'Insurance', 'Loans', 'Credit Cards'],
            'saved_payees': [],
            'payment_history': payment_history
        }

        # Generate CSRF token safely
        try:
            csrf_token = generate_csrf()
        except Exception as csrf_error:
            logger.error(f"CSRF token generation error: {csrf_error}")
            csrf_token = ''

        return render_template('banking/bill_payment.html', 
                             bill_data=bill_data,
                             page_title='Bill Payment',
                             csrf_token=csrf_token)
    except Exception as e:
        logger.error(f"Bill payment error: {str(e)} - User: {current_user.id}")
        flash('Unable to load bill payment. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Duplicate functions removed - using originals from earlier in the file
        width, height = letter

