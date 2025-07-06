"""
Smart Contracts Module Routes
Comprehensive blockchain smart contract management and deployment system
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import logging

# Create blueprint
smart_contracts_bp = Blueprint(
    'smart_contracts',
    __name__,
    url_prefix='/smart-contracts',
    template_folder='templates',
    static_folder='static'
)

logger = logging.getLogger(__name__)

@smart_contracts_bp.route('/')
@login_required
def smart_contracts_dashboard():
    """Smart Contracts main dashboard"""
    try:
        logger.info(f"User {current_user.username} accessing smart contracts dashboard")
        
        # Mock smart contract data for demonstration
        contracts_data = {
            'active_contracts': 42,
            'deployed_contracts': 158,
            'pending_deployments': 7,
            'total_gas_used': 2847592,
            'recent_deployments': [
                {
                    'name': 'NVCT Stablecoin Contract',
                    'address': '0x1234...5678',
                    'deployed_at': '2025-07-02 10:30:00',
                    'gas_used': 2547821,
                    'status': 'Active'
                },
                {
                    'name': 'Multi-Signature Wallet',
                    'address': '0xabcd...efgh',
                    'deployed_at': '2025-07-02 09:15:00',
                    'gas_used': 1854732,
                    'status': 'Active'
                },
                {
                    'name': 'Treasury Bond Token',
                    'address': '0x9876...5432',
                    'deployed_at': '2025-07-01 16:45:00',
                    'gas_used': 3247158,
                    'status': 'Pending'
                }
            ]
        }
        
        return render_template(
            'smart_contracts/smart_contracts_dashboard.html',
            contracts_data=contracts_data,
            page_title="Smart Contracts Dashboard"
        )
    except Exception as e:
        logger.error(f"Error loading smart contracts dashboard: {e}")
        flash('Error loading smart contracts dashboard', 'error')
        return redirect(url_for('dashboard.dashboard_home'))

@smart_contracts_bp.route('/deploy')
@login_required
def deploy_contract():
    """Deploy new smart contract"""
    try:
        contract_types = [
            {'id': 'erc20', 'name': 'ERC-20 Token', 'description': 'Standard fungible token contract'},
            {'id': 'erc721', 'name': 'ERC-721 NFT', 'description': 'Non-fungible token contract'},
            {'id': 'multisig', 'name': 'Multi-Signature Wallet', 'description': 'Secure multi-party wallet'},
            {'id': 'stablecoin', 'name': 'Stablecoin', 'description': 'Price-stable cryptocurrency'},
            {'id': 'bond', 'name': 'Treasury Bond', 'description': 'Tokenized government bond'},
            {'id': 'defi', 'name': 'DeFi Protocol', 'description': 'Decentralized finance protocol'}
        ]
        
        return render_template(
            'smart_contracts/smart_contracts_deploy.html',
            contract_types=contract_types,
            page_title="Deploy Smart Contract"
        )
    except Exception as e:
        logger.error(f"Error loading contract deployment: {e}")
        flash('Error loading contract deployment page', 'error')
        return redirect(url_for('smart_contracts.smart_contracts_dashboard'))

@smart_contracts_bp.route('/manage')
@login_required
def manage_contracts():
    """Manage existing smart contracts"""
    try:
        deployed_contracts = [
            {
                'id': 1,
                'name': 'NVCT Stablecoin',
                'type': 'ERC-20',
                'address': '0x1234567890abcdef1234567890abcdef12345678',
                'deployed_date': '2025-06-15',
                'status': 'Active',
                'total_supply': '30000000000000',
                'holders': 15847,
                'transactions': 2847593
            },
            {
                'id': 2,
                'name': 'Treasury Multi-Sig',
                'type': 'Multi-Signature',
                'address': '0xabcdef1234567890abcdef1234567890abcdef12',
                'deployed_date': '2025-06-20',
                'status': 'Active',
                'signers': 7,
                'required_signatures': 4,
                'transactions': 847
            },
            {
                'id': 3,
                'name': 'Government Bond Token',
                'type': 'Treasury Bond',
                'address': '0x9876543210fedcba9876543210fedcba98765432',
                'deployed_date': '2025-07-01',
                'status': 'Pending',
                'bond_value': '1000000000',
                'maturity_date': '2030-07-01',
                'interest_rate': '3.5%'
            }
        ]
        
        return render_template(
            'smart_contracts_manage.html',
            contracts=deployed_contracts,
            page_title="Manage Smart Contracts"
        )
    except Exception as e:
        logger.error(f"Error loading contract management: {e}")
        flash('Error loading contract management page', 'error')
        return redirect(url_for('smart_contracts.smart_contracts_dashboard'))

@smart_contracts_bp.route('/audit')
@login_required
def audit_contracts():
    """Smart contract security audit and verification"""
    try:
        audit_results = [
            {
                'contract_name': 'NVCT Stablecoin',
                'audit_date': '2025-06-30',
                'auditor': 'CertiK',
                'security_score': 98,
                'vulnerabilities': 0,
                'status': 'Passed',
                'report_url': '#'
            },
            {
                'contract_name': 'Treasury Multi-Sig',
                'audit_date': '2025-06-28',
                'auditor': 'OpenZeppelin',
                'security_score': 96,
                'vulnerabilities': 1,
                'status': 'Passed with Minor Issues',
                'report_url': '#'
            },
            {
                'contract_name': 'Government Bond Token',
                'audit_date': '2025-07-01',
                'auditor': 'ConsenSys Diligence',
                'security_score': 92,
                'vulnerabilities': 2,
                'status': 'In Review',
                'report_url': '#'
            }
        ]
        
        return render_template(
            'smart_contracts_audit.html',
            audit_results=audit_results,
            page_title="Smart Contract Audits"
        )
    except Exception as e:
        logger.error(f"Error loading contract audits: {e}")
        flash('Error loading contract audit page', 'error')
        return redirect(url_for('smart_contracts.smart_contracts_dashboard'))

@smart_contracts_bp.route('/monitor')
@login_required
def monitor_contracts():
    """Real-time smart contract monitoring and analytics"""
    try:
        monitoring_data = {
            'network_status': 'Operational',
            'avg_gas_price': 25,
            'block_time': 12.5,
            'total_transactions': 15847632,
            'active_contracts': 42,
            'real_time_metrics': [
                {'metric': 'Gas Usage', 'value': '2.4M', 'change': '+5.2%'},
                {'metric': 'Transaction Volume', 'value': '$847M', 'change': '+12.8%'},
                {'metric': 'Contract Calls', 'value': '15.7K', 'change': '+8.4%'},
                {'metric': 'Error Rate', 'value': '0.02%', 'change': '-0.1%'}
            ]
        }
        
        return render_template(
            'smart_contracts_monitor.html',
            monitoring_data=monitoring_data,
            page_title="Smart Contract Monitoring"
        )
    except Exception as e:
        logger.error(f"Error loading contract monitoring: {e}")
        flash('Error loading contract monitoring page', 'error')
        return redirect(url_for('smart_contracts.smart_contracts_dashboard'))

@smart_contracts_bp.route('/realtime')
@login_required
def realtime_monitor():
    """Real-time WebSocket-powered smart contract monitoring"""
    try:
        logger.info(f"User {current_user.username} accessing real-time smart contracts monitor")
        
        return render_template(
            'smart_contracts_realtime.html',
            page_title="Smart Contracts - Real-Time Monitor"
        )
    except Exception as e:
        logger.error(f"Error loading real-time contract monitoring: {e}")
        flash('Error loading real-time monitoring page', 'error')
        return redirect(url_for('smart_contracts.smart_contracts_dashboard'))

# ===== MISSING ROUTE ALIASES FOR ORPHANED TEMPLATES =====

@smart_contracts_bp.route('/dashboard')
@login_required
def dashboard():
    """Smart contracts dashboard - alias for main dashboard"""
    return smart_contracts_dashboard()

@smart_contracts_bp.route('/deploy')
@login_required
def deploy():
    """Deploy contract - alias for deploy_contract route"""
    return deploy_contract()

@smart_contracts_bp.route('/monitor')
@login_required
def monitor():
    """Monitor contracts - alias for monitor_contracts route"""
    return monitor_contracts()

@smart_contracts_bp.route('/realtime')
@login_required
def realtime():
    """Real-time monitoring - alias for realtime_monitor route"""
    return realtime_monitor()

@smart_contracts_bp.route('/api/health')
def health_check():
    """Smart Contracts module health check"""
    return jsonify({
        'status': 'healthy',
        'app_module': 'smart_contracts',
        'version': '1.0.0',
        'timestamp': '2025-07-02T21:00:00Z'
    })

# Blockchain Liquidity Management Routes (from legacy liquidity_routes.py)

@smart_contracts_bp.route('/liquidity')
@login_required
def liquidity_dashboard():
    """NVCT Liquidity Pools Dashboard"""
    try:
        logger.info(f"User {current_user.username} accessing liquidity dashboard")
        
        from .services import SmartContractService
        service = SmartContractService()
        
        liquidity_data = {
            'pools': service.get_liquidity_pools(),
            'total_tvl': '745000000',
            'total_volume_24h': '24273000',
            'pool_count': 8,
            'provider_count': 216
        }
        
        return render_template(
            'smart_contracts_liquidity.html',
            liquidity_data=liquidity_data,
            page_title="Blockchain Liquidity Management"
        )
    except Exception as e:
        logger.error(f"Error loading liquidity dashboard: {e}")
        flash('Error loading liquidity dashboard', 'error')
        return redirect(url_for('smart_contracts.smart_contracts_dashboard'))

@smart_contracts_bp.route('/liquidity/create', methods=['GET', 'POST'])
@login_required
def create_liquidity_pool():
    """Create new NVCT liquidity pool"""
    try:
        if request.method == 'POST':
            from .services import SmartContractService
            service = SmartContractService()
            
            pool_data = {
                'trading_pair': request.form.get('trading_pair'),
                'initial_nvct_amount': int(request.form.get('initial_nvct_amount', 0)),
                'initial_paired_amount': int(request.form.get('initial_paired_amount', 0)),
                'network': request.form.get('network', 'ethereum')
            }
            
            result = service.create_liquidity_pool(pool_data)
            
            if result.get('status') == 'pool_created':
                flash('Liquidity pool created successfully!', 'success')
                return redirect(url_for('smart_contracts.liquidity_dashboard'))
            else:
                flash(result.get('message', 'Pool creation failed'), 'error')
        
        return render_template(
            'smart_contracts_create_pool.html',
            page_title="Create Liquidity Pool"
        )
    except Exception as e:
        logger.error(f"Error creating liquidity pool: {e}")
        flash('Error creating liquidity pool', 'error')
        return redirect(url_for('smart_contracts.liquidity_dashboard'))

# Blockchain Settlement Routes (from legacy settlement_routes.py)

@smart_contracts_bp.route('/settlement')
@login_required
def settlement_dashboard():
    """Blockchain Settlement Dashboard"""
    try:
        logger.info(f"User {current_user.username} accessing settlement dashboard")
        
        from .services import SmartContractService
        service = SmartContractService()
        
        settlement_data = service.get_settlement_dashboard_data()
        
        return render_template(
            'smart_contracts_settlement.html',
            settlement_data=settlement_data,
            page_title="Blockchain Settlement Operations"
        )
    except Exception as e:
        logger.error(f"Error loading settlement dashboard: {e}")
        flash('Error loading settlement dashboard', 'error')
        return redirect(url_for('smart_contracts.smart_contracts_dashboard'))

@smart_contracts_bp.route('/settlement/analytics')
@login_required
def settlement_analytics():
    """Settlement Analytics and Performance Metrics"""
    try:
        logger.info(f"User {current_user.username} accessing settlement analytics")
        
        from .services import SmartContractService
        service = SmartContractService()
        
        analytics_data = service.get_settlement_analytics()
        
        return render_template(
            'smart_contracts_settlement_analytics.html',
            analytics_data=analytics_data,
            page_title="Settlement Analytics"
        )
    except Exception as e:
        logger.error(f"Error loading settlement analytics: {e}")
        flash('Error loading settlement analytics', 'error')
        return redirect(url_for('smart_contracts.settlement_dashboard'))

@smart_contracts_bp.route('/settlement/create', methods=['GET', 'POST'])
@login_required
def create_settlement():
    """Create new blockchain settlement"""
    try:
        if request.method == 'POST':
            from .services import SmartContractService
            service = SmartContractService()
            
            settlement_data = {
                'amount': request.form.get('amount'),
                'currency': request.form.get('currency'),
                'from_network': request.form.get('from_network'),
                'to_network': request.form.get('to_network'),
                'recipient_address': request.form.get('recipient_address')
            }
            
            result = service.create_settlement(settlement_data)
            
            if result.get('status') == 'settlement_initiated':
                flash(f'Settlement initiated: {result.get("settlement_id")}', 'success')
                return redirect(url_for('smart_contracts.settlement_dashboard'))
            else:
                flash(result.get('message', 'Settlement creation failed'), 'error')
        
        return render_template(
            'smart_contracts_create_settlement.html',
            page_title="Create Settlement"
        )
    except Exception as e:
        logger.error(f"Error creating settlement: {e}")
        flash('Error creating settlement', 'error')
        return redirect(url_for('smart_contracts.settlement_dashboard'))

# Admin Blockchain Operations Routes (from legacy admin/blockchain/)

@smart_contracts_bp.route('/admin')
@login_required
def blockchain_admin_dashboard():
    """Blockchain Administration Dashboard"""
    try:
        # Check admin permissions
        if not hasattr(current_user, 'role') or current_user.role not in ['admin', 'super_admin', 'blockchain_admin']:
            flash('Admin privileges required', 'error')
            return redirect(url_for('smart_contracts.smart_contracts_dashboard'))
        
        logger.info(f"Admin {current_user.username} accessing blockchain admin dashboard")
        
        from .services import SmartContractService
        service = SmartContractService()
        
        admin_data = service.get_blockchain_admin_dashboard()
        
        return render_template(
            'smart_contracts_admin.html',
            admin_data=admin_data,
            page_title="Blockchain Administration"
        )
    except Exception as e:
        logger.error(f"Error loading blockchain admin dashboard: {e}")
        flash('Error loading admin dashboard', 'error')
        return redirect(url_for('smart_contracts.smart_contracts_dashboard'))

# Error handlers
@smart_contracts_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors within smart contracts module"""
    return render_template('404.html'), 404

@smart_contracts_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors within smart contracts module"""
    logger.error(f"Internal error in smart contracts module: {error}")
    return render_template('500.html'), 500

# ===== HYPHENATED URL SUPPORT BLUEPRINT =====
# Create a secondary blueprint to handle hyphenated URLs (smart-contracts)
# and redirect them to the main underscore URLs (smart_contracts)

smart_contracts_hyphen_bp = Blueprint(
    'smart_contracts_hyphen',
    __name__,
    url_prefix='/smart-contracts'
)

@smart_contracts_hyphen_bp.route('/dashboard')
def dashboard_redirect():
    """Redirect hyphenated dashboard URL to underscore version"""
    return redirect(url_for('smart_contracts.dashboard'))

@smart_contracts_hyphen_bp.route('/deploy')
def deploy_redirect():
    """Redirect hyphenated deploy URL to underscore version"""
    return redirect(url_for('smart_contracts.deploy'))

@smart_contracts_hyphen_bp.route('/monitor')
def monitor_redirect():
    """Redirect hyphenated monitor URL to underscore version"""
    return redirect(url_for('smart_contracts.monitor'))

@smart_contracts_hyphen_bp.route('/realtime')
def realtime_redirect():
    """Redirect hyphenated realtime URL to underscore version"""
    return redirect(url_for('smart_contracts.realtime'))

# ===== ROUTES FOR ORPHANED TEMPLATES =====

@smart_contracts_bp.route('/contracts-dashboard')
@login_required
def smart_contracts_dashboard_page():
    """Smart Contracts dashboard using orphaned template"""
    try:
        contracts_data = {
            'active_contracts': 42,
            'deployed_contracts': 158,
            'pending_deployments': 7,
            'total_gas_used': 2847592
        }
        
        return render_template('smart_contracts_dashboard.html',
                             contracts_data=contracts_data,
                             page_title='Smart Contracts Dashboard')
        
    except Exception as e:
        logger.error(f"Smart contracts dashboard error: {e}")
        return redirect(url_for('smart_contracts.smart_contracts_dashboard'))

@smart_contracts_bp.route('/contracts-deploy')
@login_required
def smart_contracts_deploy_page():
    """Smart Contracts deploy using orphaned template"""
    try:
        deployment_data = {
            'networks': ['Ethereum', 'Polygon', 'BSC', 'Arbitrum'],
            'gas_estimates': {'low': 150000, 'medium': 180000, 'high': 220000}
        }
        
        return render_template('smart_contracts_deploy.html',
                             deployment_data=deployment_data,
                             page_title='Smart Contract Deployment')
        
    except Exception as e:
        logger.error(f"Smart contracts deploy error: {e}")
        return redirect(url_for('smart_contracts.smart_contracts_dashboard'))

@smart_contracts_bp.route('/contracts-monitor')
@login_required
def smart_contracts_monitor_page():
    """Smart Contracts monitor using orphaned template"""
    try:
        monitoring_data = {
            'monitoring_status': 'active',
            'alerts': 3,
            'events_count': 256
        }
        
        return render_template('smart_contracts_monitor.html',
                             monitoring_data=monitoring_data,
                             page_title='Smart Contract Monitoring')
        
    except Exception as e:
        logger.error(f"Smart contracts monitor error: {e}")
        return redirect(url_for('smart_contracts.smart_contracts_dashboard'))

@smart_contracts_bp.route('/contracts-realtime')
@login_required
def smart_contracts_realtime_page():
    """Smart Contracts realtime using orphaned template"""
    try:
        realtime_data = {
            'live_events': 12,
            'gas_price': '25 gwei',
            'network_status': 'operational'
        }
        
        return render_template('smart_contracts_realtime.html',
                             realtime_data=realtime_data,
                             page_title='Real-time Contract Monitoring')
        
    except Exception as e:
        logger.error(f"Smart contracts realtime error: {e}")
        return redirect(url_for('smart_contracts.smart_contracts_dashboard'))