"""
Interest Rate Management Routes
Comprehensive interest rate setting and control endpoints
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from typing import Dict, Any, List
from .services import InterestRateManagementService
from modules.utils.services import ErrorLoggerService
from .forms import (
    FederalRateForm, ConsumerRateForm, CommercialRateForm, 
    DepositRateForm, RateApprovalForm, BulkRateUpdateForm
)
from ..auth.models import UserRole
import logging

# Initialize services
rate_service = InterestRateManagementService()
error_logger = ErrorLoggerService()
logger = logging.getLogger(__name__)

# Create blueprint with hyphenated URL for professional banking appearance
interest_rate_management_bp = Blueprint('interest_rate_management', __name__, 
                                      url_prefix='/interest-rate-management',
                                      template_folder='templates',
                                      static_folder='static')

# Create legacy redirect blueprint for hyphenated URL
interest_rate_management_hyphen_bp = Blueprint('interest_rate_management_hyphen', __name__, 
                                      url_prefix='/interest-rate-management',
                                      template_folder='templates',
                                      static_folder='static')

# Create legacy redirect blueprint for underscore URL
interest_rate_management_legacy_bp = Blueprint('interest_rate_management_legacy', __name__, 
                                      url_prefix='/interest_rate_management',
                                      template_folder='templates',
                                      static_folder='static')

def _has_rate_authority(user) -> bool:
    """Check if user has any rate management authority"""
    authorized_roles = [
        UserRole.TREASURY_OFFICER.value,
        UserRole.ASSET_LIABILITY_MANAGER.value,
        UserRole.ADMIN.value,
        UserRole.SUPER_ADMIN.value,
        'cfo',
        'board_member',
        'monetary_policy_committee'
    ]
    return user.role in authorized_roles

def _get_user_rate_authority(user) -> Dict[str, Any]:
    """Get user's rate change authority and limits"""
    authority_matrix = {
        UserRole.TREASURY_OFFICER.value: {
            'max_change': 0.50,
            'level': 'treasury_officer',
            'products': ['savings', 'checking', 'personal_loans', 'promotional_rates']
        },
        UserRole.ASSET_LIABILITY_MANAGER.value: {
            'max_change': 1.00,
            'level': 'asset_liability_manager',
            'products': ['mortgages', 'commercial_loans', 'deposits', 'money_market', 'cds']
        },
        'cfo': {
            'max_change': 2.00,
            'level': 'cfo',
            'products': ['institutional', 'policy_rates', 'emergency_rates']
        },
        'board_member': {
            'max_change': 5.00,
            'level': 'board_member',
            'products': ['all']
        },
        UserRole.ADMIN.value: {
            'max_change': 1.00,
            'level': 'admin',
            'products': ['all']
        },
        UserRole.SUPER_ADMIN.value: {
            'max_change': 10.00,
            'level': 'super_admin',
            'products': ['all']
        }
    }
    return authority_matrix.get(user.role, {'max_change': 0.00, 'level': 'none', 'products': []})

@interest_rate_management_bp.route('/')
@login_required
def main_dashboard():
    """Interest Rate Management main dashboard - role-based routing"""
    try:
        # Check user authorization for rate management
        if not _has_rate_authority(current_user):
            flash('Access denied. You do not have rate management authority.', 'error')
            return redirect(url_for('dashboard.main_dashboard'))
        
        # Route to role-specific dashboard
        user_authority = _get_user_rate_authority(current_user)
        
        if current_user.role == UserRole.SUPER_ADMIN.value:
            # Super admin gets full access to comprehensive dashboard
            return redirect(url_for('interest_rate_management.asset_liability_manager_dashboard'))
        elif current_user.role == UserRole.ADMIN.value:
            # Admin gets access to ALM dashboard for comprehensive oversight
            return redirect(url_for('interest_rate_management.asset_liability_manager_dashboard'))
        elif current_user.role == UserRole.TREASURY_OFFICER.value:
            return redirect(url_for('interest_rate_management.treasury_officer_dashboard'))
        elif current_user.role == UserRole.ASSET_LIABILITY_MANAGER.value:
            return redirect(url_for('interest_rate_management.asset_liability_manager_dashboard'))
        elif current_user.role in ['cfo', 'board_member']:
            return redirect(url_for('interest_rate_management.asset_liability_manager_dashboard'))
        else:
            return redirect(url_for('interest_rate_management.treasury_officer_dashboard'))
            
    except Exception as e:
        error_logger.log_error("DASHBOARD_ERROR", f"Error in interest rate main dashboard: {str(e)}", 
                               {"user": str(current_user.id) if current_user.is_authenticated else None})
        return render_template('interest_rate_management/interest_rate_dashboard.html', 
                             error_message="Unable to load rate management dashboard")

@interest_rate_management_bp.route('/treasury-officer')
@login_required
def treasury_officer_dashboard():
    """Treasury Officer dashboard with consumer rate management"""
    try:
        # Verify role access
        if current_user.role != UserRole.TREASURY_OFFICER.value:
            flash('Access denied. Treasury Officer role required.', 'error')
            return redirect(url_for('interest_rate_management.main_dashboard'))
        
        # Get dashboard data
        dashboard_data = rate_service.get_treasury_officer_dashboard_data()
        
        return render_template(
            'interest_rate_management/treasury_officer_dashboard.html',
            **dashboard_data
        )
        
    except Exception as e:
        error_logger.log_error("DASHBOARD_ERROR", f"Error in treasury officer dashboard: {str(e)}", 
                               {"user": str(current_user.id)})
        return render_template('error.html', 
                             error_message="Unable to load treasury officer dashboard")

@interest_rate_management_bp.route('/asset-liability-manager')
@login_required
def asset_liability_manager_dashboard():
    """Asset Liability Manager dashboard with strategic rate management"""
    try:
        # Verify role access
        if current_user.role != UserRole.ASSET_LIABILITY_MANAGER.value:
            flash('Access denied. Asset Liability Manager role required.', 'error')
            return redirect(url_for('interest_rate_management.main_dashboard'))
        
        # Get comprehensive ALM dashboard data
        dashboard_data = rate_service.get_alm_dashboard_data()
        
        return render_template(
            'asset_liability_manager_dashboard.html',
            **dashboard_data
        )
        
    except Exception as e:
        error_logger.log_error(
            message=f"Error in ALM dashboard: {str(e)}",
            user_id=str(current_user.id),
            error_type="DASHBOARD_ERROR"
        )
        return render_template('error.html', 
                             error_message="Unable to load ALM dashboard")

@interest_rate_management_bp.route('/manage/consumer-rates', methods=['GET', 'POST'])
@login_required
def manage_consumer_rates():
    """Manage consumer banking rates (Treasury Officer authority)"""
    try:
        # Check authority
        user_authority = _get_user_rate_authority(current_user)
        if user_authority['max_change'] < 0.25:
            flash('Insufficient authority for consumer rate management.', 'error')
            return redirect(url_for('interest_rate_management.main_dashboard'))
        
        form = ConsumerRateForm(user_role=current_user.role)
        
        if form.validate_on_submit():
            # Process rate change request
            rate_change_data = {
                'product_type': form.product_type.data,
                'credit_tier': form.credit_tier.data,
                'current_rate': form.current_rate.data,
                'new_rate': form.new_rate.data,
                'ltv_ratio': form.ltv_ratio.data,
                'term_months': form.term_months.data,
                'effective_date': form.effective_date.data,
                'justification': form.rate_justification.data,
                'competitive_analysis': form.competitive_analysis.data,
                'requested_by': current_user.id
            }
            
            result = rate_service.submit_consumer_rate_change(rate_change_data)
            
            if result['success']:
                flash(f'Consumer rate change submitted successfully. Request ID: {result["request_id"]}', 'success')
                return redirect(url_for('interest_rate_management.treasury_officer_dashboard'))
            else:
                flash(f'Error submitting rate change: {result["error"]}', 'error')
        
        # Get current consumer rates for form population
        consumer_rates = rate_service.get_consumer_rates()
        
        return render_template(
            'manage_consumer_rates.html',
            form=form,
            consumer_rates=consumer_rates,
            user_authority=user_authority
        )
        
    except Exception as e:
        error_logger.log_error(
            message=f"Error in consumer rate management: {str(e)}",
            user_id=str(current_user.id),
            error_type="RATE_MANAGEMENT_ERROR"
        )
        return render_template('error.html', 
                             error_message="Unable to process consumer rate management request")

@interest_rate_management_bp.route('/manage/commercial-rates', methods=['GET', 'POST'])
@login_required
def manage_commercial_rates():
    """Manage commercial banking rates (ALM authority)"""
    try:
        # Check authority (ALM level required)
        user_authority = _get_user_rate_authority(current_user)
        if user_authority['max_change'] < 1.00:
            flash('Asset Liability Manager authority required for commercial rates.', 'error')
            return redirect(url_for('interest_rate_management.main_dashboard'))
        
        form = CommercialRateForm(user_role=current_user.role)
        
        if form.validate_on_submit():
            # Process commercial rate change
            rate_change_data = {
                'product_type': form.product_type.data,
                'business_size': form.business_size.data,
                'risk_rating': form.risk_rating.data,
                'current_rate': form.current_rate.data,
                'new_rate': form.new_rate.data,
                'loan_amount_range': form.loan_amount_range.data,
                'effective_date': form.effective_date.data,
                'credit_analysis': form.credit_analysis.data,
                'profitability_impact': form.profitability_impact.data,
                'requested_by': current_user.id
            }
            
            result = rate_service.submit_commercial_rate_change(rate_change_data)
            
            if result['success']:
                flash(f'Commercial rate change submitted successfully. Request ID: {result["request_id"]}', 'success')
                return redirect(url_for('interest_rate_management.asset_liability_manager_dashboard'))
            else:
                flash(f'Error submitting rate change: {result["error"]}', 'error')
        
        # Get current commercial rates
        commercial_rates = rate_service.get_commercial_rates()
        
        return render_template(
            'manage_commercial_rates.html',
            form=form,
            commercial_rates=commercial_rates,
            user_authority=user_authority
        )
        
    except Exception as e:
        error_logger.log_error(
            message=f"Error in commercial rate management: {str(e)}",
            user_id=str(current_user.id),
            error_type="RATE_MANAGEMENT_ERROR"
        )
        return render_template('error.html', 
                             error_message="Unable to process commercial rate management request")

@interest_rate_management_bp.route('/approve/rate-changes')
@login_required
def rate_change_approvals():
    """Rate change approval interface for authorized personnel"""
    try:
        # Check approval authority
        user_authority = _get_user_rate_authority(current_user)
        if user_authority['level'] not in ['asset_liability_manager', 'cfo', 'board_member', 'admin', 'super_admin']:
            flash('Insufficient authority for rate change approvals.', 'error')
            return redirect(url_for('interest_rate_management.main_dashboard'))
        
        # Get pending rate change requests for approval
        pending_requests = rate_service.get_pending_rate_changes_for_approval(
            approver_level=user_authority['level']
        )
        
        return render_template(
            'rate_change_approvals.html',
            pending_requests=pending_requests,
            user_authority=user_authority
        )
        
    except Exception as e:
        error_logger.log_error(
            message=f"Error in rate change approvals: {str(e)}",
            user_id=str(current_user.id),
            error_type="APPROVAL_ERROR"
        )
        return render_template('error.html', 
                             error_message="Unable to load rate change approvals")

@interest_rate_management_bp.route('/approve/rate-change/<request_id>', methods=['POST'])
@login_required 
def process_rate_approval(request_id):
    """Process individual rate change approval"""
    try:
        # Check approval authority
        user_authority = _get_user_rate_authority(current_user)
        if user_authority['level'] not in ['asset_liability_manager', 'cfo', 'board_member', 'admin', 'super_admin']:
            return jsonify({'success': False, 'error': 'Insufficient approval authority'})
        
        approval_data = {
            'request_id': request_id,
            'approver_id': current_user.id,
            'approval_action': request.json.get('action'),
            'approval_notes': request.json.get('notes'),
            'conditions': request.json.get('conditions'),
            'risk_assessment': request.json.get('risk_assessment'),
            'approval_level': user_authority['level'],
            'approval_authority': user_authority['max_change']
        }
        
        result = rate_service.process_rate_change_approval(approval_data)
        
        return jsonify(result)
        
    except Exception as e:
        error_logger.log_error(
            message=f"Error processing rate approval: {str(e)}",
            user_id=str(current_user.id),
            error_type="APPROVAL_ERROR"
        )
        return jsonify({'success': False, 'error': 'Unable to process approval'})

@interest_rate_management_bp.route('/bulk-update', methods=['GET', 'POST'])
@login_required
def bulk_rate_update():
    """Bulk rate update interface (high authority required)"""
    try:
        # Check high-level authority
        user_authority = _get_user_rate_authority(current_user)
        if user_authority['level'] not in ['cfo', 'board_member', 'super_admin']:
            flash('CFO/Board level authority required for bulk rate updates.', 'error')
            return redirect(url_for('interest_rate_management.main_dashboard'))
        
        form = BulkRateUpdateForm(user_role=current_user.role)
        
        if form.validate_on_submit():
            # Process bulk rate update
            bulk_update_data = {
                'product_category': form.product_category.data,
                'adjustment_type': form.adjustment_type.data,
                'adjustment_value': form.adjustment_value.data,
                'effective_date': form.effective_date.data,
                'justification': form.justification.data,
                'fed_policy_correlation': form.fed_policy_correlation.data,
                'requested_by': current_user.id
            }
            
            result = rate_service.execute_bulk_rate_update(bulk_update_data)
            
            if result['success']:
                flash(f'Bulk rate update executed successfully. {result["affected_products"]} products updated.', 'success')
                return redirect(url_for('interest_rate_management.main_dashboard'))
            else:
                flash(f'Error executing bulk update: {result["error"]}', 'error')
        
        return render_template(
            'bulk_rate_update.html',
            form=form,
            user_authority=user_authority
        )
        
    except Exception as e:
        error_logger.log_error(
            message=f"Error in bulk rate update: {str(e)}",
            user_id=str(current_user.id),
            error_type="BULK_UPDATE_ERROR"
        )
        return render_template('error.html', 
                             error_message="Unable to process bulk rate update")
        
        # Get comprehensive rate data
        central_bank_rates = rate_service.get_central_bank_rates()
        lending_rates = rate_service.get_lending_rates_structure()
        deposit_rates = rate_service.get_deposit_rates_structure()
        rate_authority = rate_service.get_rate_setting_authority()
        
        return render_template('interest_rate_dashboard.html',
                             central_bank_rates=central_bank_rates,
                             lending_rates=lending_rates,
                             deposit_rates=deposit_rates,
                             rate_authority=rate_authority)
    except Exception as e:
        error_logger.log_error("interest_rate_dashboard_error", str(e))
        flash("Unable to load interest rate dashboard", "error")
        return redirect(url_for('public.index'))

# ===== ROUTES FOR ORPHANED TEMPLATES =====

@interest_rate_management_bp.route('/treasury-officer')
@login_required
def treasury_officer_dashboard_page():
    """Treasury officer dashboard using orphaned template"""
    try:
        if current_user.role != UserRole.TREASURY_OFFICER.value:
            flash('Treasury Officer access required', 'error')
            return redirect(url_for('interest_rate_management.rate_dashboard'))
        
        dashboard_data = rate_service.get_treasury_officer_dashboard_data(current_user.id)
        
        return render_template('treasury_officer_dashboard.html',
                             dashboard_data=dashboard_data,
                             page_title='Treasury Officer Dashboard')
    except Exception as e:
        error_logger.log_error("TREASURY_DASHBOARD_ERROR", str(e), {"user": current_user.id})
        flash('Error loading Treasury Officer dashboard', 'error')
        return redirect(url_for('interest_rate_management.rate_dashboard'))

@interest_rate_management_bp.route('/asset-liability-manager')
@login_required
def asset_liability_manager_dashboard_page():
    """Asset liability manager dashboard using orphaned template"""
    try:
        if current_user.role != UserRole.ASSET_LIABILITY_MANAGER.value:
            flash('Asset Liability Manager access required', 'error')
            return redirect(url_for('interest_rate_management.rate_dashboard'))
        
        dashboard_data = rate_service.get_alm_dashboard_data(current_user.id)
        
        return render_template('asset_liability_manager_dashboard.html',
                             dashboard_data=dashboard_data,
                             page_title='Asset Liability Manager Dashboard')
    except Exception as e:
        error_logger.log_error("ALM_DASHBOARD_ERROR", str(e), {"user": current_user.id})
        flash('Error loading Asset Liability Manager dashboard', 'error')
        return redirect(url_for('interest_rate_management.rate_dashboard'))

@interest_rate_management_bp.route('/lending_rates')
@login_required
def lending_rates():
    """Lending rates management"""
    try:
        if not _has_rate_authority(current_user):
            flash("Insufficient privileges for rate management", "error")
            return redirect(url_for('interest_rate_management.main_dashboard'))
        
        lending_rates_data = rate_service.get_lending_rates_structure()
        rate_authority = rate_service.get_rate_setting_authority()
        
        return render_template('lending_rates_management.html',
                             lending_rates=lending_rates_data,
                             rate_authority=rate_authority)
    except Exception as e:
        error_logger.log_error("lending_rates_error", str(e))
        flash("Unable to load lending rates", "error")
        return redirect(url_for('interest_rate_management.main_dashboard'))

@interest_rate_management_bp.route('/deposit_rates')
@login_required
def deposit_rates():
    """Deposit rates management"""
    try:
        if not _has_rate_authority(current_user):
            flash("Insufficient privileges for rate management", "error")
            return redirect(url_for('interest_rate_management.main_dashboard'))
        
        deposit_rates_data = rate_service.get_deposit_rates_structure()
        rate_authority = rate_service.get_rate_setting_authority()
        
        return render_template('deposit_rates_management.html',
                             deposit_rates=deposit_rates_data,
                             rate_authority=rate_authority)
    except Exception as e:
        error_logger.log_error("deposit_rates_error", str(e))
        flash("Unable to load deposit rates", "error")
        return redirect(url_for('interest_rate_management.main_dashboard'))

@interest_rate_management_bp.route('/rate_history')
@login_required
def rate_history():
    """Historical rate data and trends"""
    try:
        if not _has_rate_authority(current_user):
            flash("Insufficient privileges for rate management", "error")
            return redirect(url_for('interest_rate_management.main_dashboard'))
        
        historical_data = rate_service.get_historical_rate_data()
        
        return render_template('rate_history.html',
                             historical_data=historical_data)
    except Exception as e:
        error_logger.log_error("rate_history_error", str(e))
        flash("Unable to load rate history", "error")
        return redirect(url_for('interest_rate_management.main_dashboard'))

@interest_rate_management_bp.route('/rate_algorithms')
@login_required
def rate_algorithms():
    """Automated rate adjustment algorithms"""
    try:
        if not _has_senior_rate_authority(current_user):
            flash("Senior authorization required for algorithm management", "error")
            return redirect(url_for('interest_rate_management.main_dashboard'))
        
        algorithms_data = rate_service.get_rate_adjustment_algorithms()
        
        return render_template('rate_algorithms.html',
                             algorithms_data=algorithms_data)
    except Exception as e:
        error_logger.log_error("rate_algorithms_error", str(e))
        flash("Unable to load rate algorithms", "error")
        return redirect(url_for('interest_rate_management.main_dashboard'))

# API Routes for rate management
@interest_rate_management_bp.route('/api/rates/current')
@login_required
def api_current_rates():
    """API endpoint for current interest rates"""
    try:
        if not _has_rate_authority(current_user):
            return jsonify({"error": "Insufficient privileges"}), 403
        
        current_rates = {
            "central_bank": rate_service.get_central_bank_rates(),
            "lending": rate_service.get_lending_rates_structure(),
            "deposits": rate_service.get_deposit_rates_structure()
        }
        return jsonify({
            "status": "success",
            "data": current_rates
        })
    except Exception as e:
        error_logger.log_error("api_current_rates_error", str(e))
        return jsonify({"error": "Unable to retrieve current rates"}), 500

@interest_rate_management_bp.route('/api/rates/authority')
@login_required
def api_rate_authority():
    """API endpoint for rate setting authority information"""
    try:
        if not _has_rate_authority(current_user):
            return jsonify({"error": "Insufficient privileges"}), 403
        
        authority_data = rate_service.get_rate_setting_authority()
        return jsonify({
            "status": "success",
            "data": authority_data
        })
    except Exception as e:
        error_logger.log_error("api_rate_authority_error", str(e))
        return jsonify({"error": "Unable to retrieve authority data"}), 500

@interest_rate_management_bp.route('/api/rates/update', methods=['POST'])
@login_required
def api_update_rates():
    """API endpoint to update interest rates"""
    try:
        if not _has_rate_authority(current_user):
            return jsonify({"error": "Insufficient privileges"}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['product_category', 'rate_changes', 'effective_date']
        if not all(field in data for field in required_fields):
            return jsonify({
                "error": "Missing required fields",
                "required": required_fields
            }), 400
        
        # Apply rate changes
        result = rate_service.apply_rate_change(
            product_category=data['product_category'],
            rate_changes=data['rate_changes'],
            authorized_by=current_user.username,
            effective_date=data['effective_date']
        )
        
        return jsonify({
            "status": "success",
            "data": result
        })
        
    except Exception as e:
        error_logger.log_error("api_update_rates_error", str(e))
        return jsonify({"error": "Unable to process rate update"}), 500

@interest_rate_management_bp.route('/api/rates/history')
@login_required
def api_rate_history():
    """API endpoint for historical rate data"""
    try:
        if not _has_rate_authority(current_user):
            return jsonify({"error": "Insufficient privileges"}), 403
        
        historical_data = rate_service.get_historical_rate_data()
        return jsonify({
            "status": "success",
            "data": historical_data
        })
    except Exception as e:
        error_logger.log_error("api_rate_history_error", str(e))
        return jsonify({"error": "Unable to retrieve rate history"}), 500

@interest_rate_management_bp.route('/api/rates/algorithms')
@login_required
def api_rate_algorithms():
    """API endpoint for rate adjustment algorithms"""
    try:
        if not _has_senior_rate_authority(current_user):
            return jsonify({"error": "Senior authorization required"}), 403
        
        algorithms_data = rate_service.get_rate_adjustment_algorithms()
        return jsonify({
            "status": "success",
            "data": algorithms_data
        })
    except Exception as e:
        error_logger.log_error("api_rate_algorithms_error", str(e))
        return jsonify({"error": "Unable to retrieve algorithms"}), 500

# Rate change approval workflow
@interest_rate_management_bp.route('/api/rates/propose_change', methods=['POST'])
@login_required
def api_propose_rate_change():
    """API endpoint to propose a rate change for approval"""
    try:
        if not _has_rate_authority(current_user):
            return jsonify({"error": "Insufficient privileges"}), 403
        
        data = request.get_json()
        
        # Validate proposal data
        required_fields = ['product_category', 'proposed_rates', 'justification', 'effective_date']
        if not all(field in data for field in required_fields):
            return jsonify({
                "error": "Missing required fields",
                "required": required_fields
            }), 400
        
        # Create rate change proposal
        proposal_id = f"PROP-{current_user.id}-{hash(str(data))%10000:04d}"
        
        proposal_result = {
            "proposal_id": proposal_id,
            "proposer": current_user.username,
            "status": "pending_approval",
            "product_category": data['product_category'],
            "current_rates": "Retrieved from system",
            "proposed_rates": data['proposed_rates'],
            "justification": data['justification'],
            "effective_date": data['effective_date'],
            "required_approvals": _get_required_approvals(data['product_category']),
            "impact_analysis": {
                "affected_customers": "To be calculated",
                "revenue_impact": "To be analyzed",
                "competitive_position": "To be assessed"
            },
            "next_steps": [
                "Rate committee review",
                "Risk assessment",
                "Competitive analysis",
                "Final approval"
            ]
        }
        
        return jsonify({
            "status": "success",
            "data": proposal_result
        })
        
    except Exception as e:
        error_logger.log_error("api_propose_rate_change_error", str(e))
        return jsonify({"error": "Unable to submit rate proposal"}), 500

# Utility functions
def _has_rate_authority(user) -> bool:
    """Check if user has basic rate management authority"""
    authorized_roles = [
        'treasury_officer', 'asset_liability_manager', 'chief_financial_officer',
        'board_of_directors', 'monetary_policy_committee', 'admin', 'super_admin'
    ]
    return hasattr(user, 'role') and user.role in authorized_roles

def _has_senior_rate_authority(user) -> bool:
    """Check if user has senior rate management authority"""
    senior_roles = [
        'chief_financial_officer', 'board_of_directors', 
        'monetary_policy_committee', 'admin', 'super_admin'
    ]
    return hasattr(user, 'role') and user.role in senior_roles

def _get_required_approvals(product_category: str) -> List[str]:
    """Get required approval roles for product category"""
    approval_matrix = {
        'consumer_deposits': ['treasury_officer', 'asset_liability_manager'],
        'consumer_lending': ['chief_financial_officer', 'asset_liability_committee'],
        'commercial_lending': ['board_of_directors', 'monetary_policy_committee'],
        'institutional_lending': ['board_of_directors', 'federal_reserve_approval']
    }
    return approval_matrix.get(product_category, ['chief_financial_officer'])