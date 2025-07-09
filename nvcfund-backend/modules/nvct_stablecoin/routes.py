"""
NVCT Stablecoin Module Routes
Comprehensive $30 trillion stablecoin management and blockchain operations
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import logging
from datetime import datetime
from .services import NVCTStablecoinService, AssetBackingService, CrossChainService

# Create blueprint with hyphenated URL for professional banking appearance
nvct_stablecoin_bp = Blueprint(
    'nvct_stablecoin',
    __name__,
    url_prefix='/nvct-stablecoin',
    template_folder='templates',
    static_folder='static'
)

# Create legacy redirect blueprint for underscore URL
nvct_stablecoin_legacy_bp = Blueprint(
    'nvct_stablecoin_legacy',
    __name__,
    url_prefix='/nvct_stablecoin',
    template_folder='templates',
    static_folder='static'
)

# Create legacy redirect blueprint for hyphenated URL
nvct_stablecoin_hyphen_bp = Blueprint(
    'nvct_stablecoin_hyphen',
    __name__,
    url_prefix='/nvct-stablecoin',
    template_folder='templates',
    static_folder='static'
)

logger = logging.getLogger(__name__)

# Initialize services
nvct_service = NVCTStablecoinService()
asset_service = AssetBackingService()
crosschain_service = CrossChainService()

@nvct_stablecoin_bp.route('/')
@nvct_stablecoin_hyphen_bp.route('/')
@login_required
def nvct_dashboard():
    """NVCT Stablecoin main dashboard"""
    try:
        logger.info(f"User {current_user.username} accessing NVCT dashboard")
        
        # Get comprehensive NVCT data
        nvct_overview = nvct_service.get_nvct_overview()
        asset_backing = asset_service.get_asset_backing_status()
        network_status = crosschain_service.get_network_deployment_status()
        supply_metrics = nvct_service.get_supply_metrics()
        
        dashboard_data = {
            'nvct_overview': nvct_overview,
            'asset_backing': asset_backing,
            'network_status': network_status,
            'supply_metrics': supply_metrics,
            'total_supply': '30,000,000,000,000',  # 30T NVCT
            'backing_value': '56,700,000,000,000',  # $56.7T backing
            'backing_ratio': '189',  # 189% over-collateralization
            'current_price': '1.00'  # $1.00 USD parity target
        }
        
        return render_template(
            'nvct_stablecoin/nvct_stablecoin_dashboard.html',
            dashboard_data=dashboard_data,
            page_title="NVCT Stablecoin Operations"
        )
    except Exception as e:
        logger.error(f"Error loading NVCT dashboard: {e}")
        flash('Error loading NVCT dashboard', 'error')
        return redirect(url_for('dashboard.dashboard_home'))

@nvct_stablecoin_bp.route('/supply')
@login_required
def supply_management():
    """NVCT supply management and minting controls"""
    try:
        supply_data = nvct_service.get_detailed_supply_data()
        minting_history = nvct_service.get_minting_history()
        burn_history = nvct_service.get_burn_history()
        
        return render_template(
            'nvct_stablecoin/nvct_supply_management.html',
            supply_data=supply_data,
            minting_history=minting_history,
            burn_history=burn_history,
            page_title="NVCT Supply Management"
        )
    except Exception as e:
        logger.error(f"Error loading supply management: {e}")
        flash('Error loading supply management page', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/assets')
@login_required
def asset_backing():
    """Asset backing dashboard with $56.7T backing portfolio"""
    try:
        backing_portfolio = asset_service.get_backing_portfolio()
        asset_allocation = asset_service.get_asset_allocation()
        valuation_reports = asset_service.get_valuation_reports()
        compliance_status = asset_service.get_compliance_status()
        
        return render_template(
            'nvct_asset_backing.html',
            backing_portfolio=backing_portfolio,
            asset_allocation=asset_allocation,
            valuation_reports=valuation_reports,
            compliance_status=compliance_status,
            page_title="NVCT Asset Backing Portfolio"
        )
    except Exception as e:
        logger.error(f"Error loading asset backing: {e}")
        flash('Error loading asset backing page', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/networks')
@login_required
def network_management():
    """Multi-chain network deployment and management"""
    try:
        deployment_status = crosschain_service.get_deployment_status()
        bridge_operations = crosschain_service.get_bridge_operations()
        network_metrics = crosschain_service.get_network_metrics()
        pending_deployments = crosschain_service.get_pending_deployments()
        
        return render_template(
            'nvct_network_management.html',
            deployment_status=deployment_status,
            bridge_operations=bridge_operations,
            network_metrics=network_metrics,
            pending_deployments=pending_deployments,
            page_title="NVCT Network Management"
        )
    except Exception as e:
        logger.error(f"Error loading network management: {e}")
        flash('Error loading network management page', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/bridge')
@login_required
def cross_chain_bridge():
    """Cross-chain bridge interface for NVCT transfers"""
    try:
        supported_chains = crosschain_service.get_supported_chains()
        bridge_fees = crosschain_service.get_bridge_fees()
        recent_transfers = crosschain_service.get_recent_bridge_transfers()
        
        return render_template(
            'nvct_cross_chain_bridge.html',
            supported_chains=supported_chains,
            bridge_fees=bridge_fees,
            recent_transfers=recent_transfers,
            page_title="NVCT Cross-Chain Bridge"
        )
    except Exception as e:
        logger.error(f"Error loading cross-chain bridge: {e}")
        flash('Error loading bridge interface', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/governance')
@login_required
def governance_dashboard():
    """NVCT governance and voting interface"""
    try:
        governance_data = nvct_service.get_governance_data()
        active_proposals = nvct_service.get_active_proposals()
        voting_history = nvct_service.get_voting_history()
        
        return render_template(
            'nvct_stablecoin/nvct_governance.html',
            governance_data=governance_data,
            active_proposals=active_proposals,
            voting_history=voting_history,
            page_title="NVCT Governance"
        )
    except Exception as e:
        logger.error(f"Error loading governance dashboard: {e}")
        flash('Error loading governance page', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/analytics')
@login_required
def nvct_analytics_dashboard():
    """NVCT analytics and performance metrics"""
    try:
        market_data = nvct_service.get_market_analytics()
        price_stability = nvct_service.get_price_stability_metrics()
        volume_data = nvct_service.get_volume_analytics()
        holder_metrics = nvct_service.get_holder_analytics()
        
        return render_template(
            'nvct_stablecoin/analytics_dashboard.html',
            market_data=market_data,
            price_stability=price_stability,
            volume_data=volume_data,
            holder_metrics=holder_metrics,
            page_title="NVCT Analytics"
        )
    except Exception as e:
        logger.error(f"Error loading analytics dashboard: {e}")
        flash('Error loading analytics page', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/mint', methods=['POST'])
@login_required
def mint_nvct():
    """Mint new NVCT tokens (restricted access)"""
    try:
        # Check user permissions for minting
        if not nvct_service.user_can_mint(current_user):
            flash('Insufficient permissions for NVCT minting', 'error')
            return redirect(url_for('nvct_stablecoin.supply_management'))
        
        amount = request.form.get('amount')
        recipient = request.form.get('recipient')
        justification = request.form.get('justification')
        
        if not amount or not recipient or not justification:
            flash('All fields required for minting operation', 'error')
            return redirect(url_for('nvct_stablecoin.supply_management'))
        
        # Execute minting operation
        result = nvct_service.mint_tokens(
            amount=float(amount),
            recipient=recipient,
            justification=justification,
            authorized_by=current_user.username
        )
        
        if result['success']:
            flash(f'Successfully minted {amount} NVCT tokens', 'success')
            logger.info(f"NVCT minting: {amount} tokens minted by {current_user.username}")
        else:
            flash(f'Minting failed: {result["error"]}', 'error')
        
        return redirect(url_for('nvct_stablecoin.supply_management'))
        
    except Exception as e:
        logger.error(f"Error in NVCT minting: {e}")
        flash('Minting operation failed', 'error')
        return redirect(url_for('nvct_stablecoin.supply_management'))

@nvct_stablecoin_bp.route('/burn', methods=['POST'])
@login_required
def burn_nvct():
    """Burn NVCT tokens to reduce supply"""
    try:
        # Check user permissions for burning
        if not nvct_service.user_can_burn(current_user):
            flash('Insufficient permissions for NVCT burning', 'error')
            return redirect(url_for('nvct_stablecoin.supply_management'))
        
        amount = request.form.get('amount')
        justification = request.form.get('justification')
        
        if not amount or not justification:
            flash('Amount and justification required for burning operation', 'error')
            return redirect(url_for('nvct_stablecoin.supply_management'))
        
        # Execute burning operation
        result = nvct_service.burn_tokens(
            amount=float(amount),
            justification=justification,
            authorized_by=current_user.username
        )
        
        if result['success']:
            flash(f'Successfully burned {amount} NVCT tokens', 'success')
            logger.info(f"NVCT burning: {amount} tokens burned by {current_user.username}")
        else:
            flash(f'Burning failed: {result["error"]}', 'error')
        
        return redirect(url_for('nvct_stablecoin.supply_management'))
        
    except Exception as e:
        logger.error(f"Error in NVCT burning: {e}")
        flash('Burning operation failed', 'error')
        return redirect(url_for('nvct_stablecoin.supply_management'))

@nvct_stablecoin_bp.route('/deploy', methods=['POST'])
@login_required
def deploy_to_network():
    """Deploy NVCT to new blockchain network"""
    try:
        # Check deployment permissions
        if not crosschain_service.user_can_deploy(current_user):
            flash('Insufficient permissions for network deployment', 'error')
            return redirect(url_for('nvct_stablecoin.network_management'))
        
        network = request.form.get('network')
        if not network:
            flash('Network selection required', 'error')
            return redirect(url_for('nvct_stablecoin.network_management'))
        
        # Execute deployment
        result = crosschain_service.deploy_to_network(
            network=network,
            deployed_by=current_user.username
        )
        
        if result['success']:
            flash(f'NVCT deployment to {network} initiated successfully', 'success')
            logger.info(f"NVCT deployment: {network} deployment by {current_user.username}")
        else:
            flash(f'Deployment failed: {result["error"]}', 'error')
        
        return redirect(url_for('nvct_stablecoin.network_management'))
        
    except Exception as e:
        logger.error(f"Error in network deployment: {e}")
        flash('Network deployment failed', 'error')
        return redirect(url_for('nvct_stablecoin.network_management'))

@nvct_stablecoin_bp.route('/stablecoin-dashboard')
@login_required
def nvct_stablecoin_dashboard_page():
    """NVCT Stablecoin dashboard using orphaned template"""
    try:
        nvct_overview = nvct_service.get_nvct_overview()
        
        return render_template('nvct_stablecoin/nvct_stablecoin_dashboard.html',
                             nvct_overview=nvct_overview,
                             page_title='NVCT Stablecoin Dashboard')
        
    except Exception as e:
        logger.error(f"NVCT dashboard error: {e}")
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/supply-operations')
@login_required
def nvct_supply_operations():
    """NVCT supply management using orphaned template"""
    try:
        supply_data = nvct_service.get_supply_metrics()
        
        return render_template('nvct_stablecoin/nvct_supply_management.html',
                             supply_data=supply_data,
                             page_title='NVCT Supply Management')
        
    except Exception as e:
        logger.error(f"NVCT supply operations error: {e}")
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/analytics-center')
@login_required
def nvct_analytics_center():
    """NVCT analytics dashboard using orphaned template"""
    try:
        analytics_data = nvct_service.get_analytics_data()
        
        return render_template('nvct_stablecoin/nvct_analytics_dashboard.html',
                             analytics_data=analytics_data,
                             page_title='NVCT Analytics Dashboard')
        
    except Exception as e:
        logger.error(f"NVCT analytics error: {e}")
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/governance-portal')
@login_required
def nvct_governance_portal():
    """NVCT governance using orphaned template"""
    try:
        governance_data = nvct_service.get_governance_data()
        
        return render_template('nvct_stablecoin/nvct_governance.html',
                             governance_data=governance_data,
                             page_title='NVCT Governance Portal')
        
    except Exception as e:
        logger.error(f"NVCT governance error: {e}")
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/api/health')
def health_check():
    """NVCT Stablecoin module health check"""
    return jsonify({
        'status': 'healthy',
        'app_module': 'nvct_stablecoin',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'total_supply': '30000000000000',
        'backing_ratio': '189%'
    })

# Error handlers
@nvct_stablecoin_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors within NVCT module"""
    return render_template('404.html'), 404

@nvct_stablecoin_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors within NVCT module"""
    logger.error(f"Internal error in NVCT module: {error}")
    return render_template('500.html'), 500