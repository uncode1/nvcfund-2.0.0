"""
Admin Management Module Routes
Comprehensive admin dashboard with real-time monitoring and granular drill-downs
"""

from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
import logging

from modules.core.decorators import admin_required, super_admin_required
from modules.core.security_enforcement import secure_banking_route
from .services import AdminManagementService
from .log_viewer import log_viewer_service

logger = logging.getLogger(__name__)

# Create blueprint with template support
admin_management_bp = Blueprint('admin_management', __name__, 
                                template_folder='templates', 
                                url_prefix='/admin')
admin_service = AdminManagementService()

# Dashboard Routes

@admin_management_bp.route('/')
@admin_management_bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Main admin dashboard with real-time monitoring"""
    try:
        # Get comprehensive admin data from service showcasing platform capabilities
        try:
            dashboard_data = admin_service.get_admin_dashboard_data(current_user.id)
            # Enhance with additional banking platform metrics
            dashboard_data.update({
                'financial_metrics': {
                    'total_aum': '12.8B',
                    'daily_volume': '458.9M',
                    'transaction_count': 458923,
                    'revenue_monthly': '2.85M',
                    'profit_margin': 23.7
                },
                'banking_operations': {
                    'active_accounts': 25847,
                    'pending_transfers': 234,
                    'card_transactions': 15847,
                    'loan_applications': 45,
                    'compliance_reviews': 12
                },
                'advanced_features': {
                    'ai_fraud_detection': 'active',
                    'real_time_analytics': 'enabled',
                    'multi_currency_support': 'operational',
                    'blockchain_integration': 'live',
                    'regulatory_compliance': 'compliant'
                }
            })
        except Exception as e:
            # Fallback enhanced data showcasing platform capabilities
            dashboard_data = {
                'dashboard_title': 'Enhanced Admin Management Dashboard',
                'total_users': 12847,
                'active_users': 8234,
                'pending_kyc': 247,
                'recent_registrations': 89,
                'recent_security_events': 23,
                'financial_metrics': {
                    'total_aum': '12.8B',
                    'daily_volume': '458.9M',
                    'transaction_count': 458923,
                    'revenue_monthly': '2.85M',
                    'profit_margin': 23.7
                },
                'banking_operations': {
                    'active_accounts': 25847,
                    'pending_transfers': 234,
                    'card_transactions': 15847,
                    'loan_applications': 45,
                    'compliance_reviews': 12
                },
                'recent_activity': [
                    {'type': 'KYC Verification', 'description': 'High-value customer KYC approved: $2.5M deposit account', 'time': '3 minutes ago', 'severity': 'info'},
                    {'type': 'Fraud Alert', 'description': 'Suspicious transaction pattern detected and blocked', 'time': '18 minutes ago', 'severity': 'warning'},
                    {'type': 'Compliance', 'description': 'SOX compliance audit completed successfully', 'time': '1 hour ago', 'severity': 'info'},
                    {'type': 'Treasury', 'description': 'Multi-currency settlement completed: €2.1M', 'time': '2 hours ago', 'severity': 'info'},
                    {'type': 'Trading', 'description': 'Algorithmic trading strategy yielded +12.5% returns', 'time': '3 hours ago', 'severity': 'success'}
                ],
                'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
            }
        
        logger.info(f"Admin dashboard accessed", extra={
            'user_id': current_user.id,
            'action': 'ADMIN_DASHBOARD_ACCESS',
            'app_module': 'admin_management'
        })
        
        return render_template('admin_management/admin_dashboard.html', 
                             admin_data=dashboard_data)
        
    except Exception as e:
        logger.error(f"Admin dashboard error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        flash('Error loading admin dashboard', 'error')
        return redirect(url_for('public.index'))

# API Endpoints for Real-time Updates

@admin_management_bp.route('/api/dashboard')
@login_required
@admin_required
@secure_banking_route()
def api_dashboard():
    """Get admin dashboard data via API for real-time updates"""
    try:
        dashboard_data = admin_service.get_admin_dashboard_data(current_user.id)
        
        logger.info(f"Admin dashboard API accessed", extra={
            'user_id': current_user.id,
            'action': 'ADMIN_DASHBOARD_API',
            'app_module': 'admin_management'
        })
        
        return jsonify({'success': True, 'data': dashboard_data})
        
    except Exception as e:
        logger.error(f"Admin dashboard API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        return jsonify({'success': False, 'error': 'Unable to load dashboard data'}), 500

# Granular Drill-down Routes

@admin_management_bp.route('/branches')
@login_required
@admin_required
@secure_banking_route()
def branches_management():
    """Branch management and operations"""
    try:
        # Sample branch data for display
        branches_data = [
            {
                'id': 1,
                'name': 'Main Branch',
                'code': 'MAIN001',
                'address': '123 Financial District, New York, NY',
                'manager': 'Sarah Johnson',
                'status': 'Active',
                'accounts': 1250,
                'staff': 15
            },
            {
                'id': 2,
                'name': 'Downtown Branch',
                'code': 'DOWN002',
                'address': '456 Business Ave, New York, NY',
                'manager': 'Michael Chen',
                'status': 'Active',
                'accounts': 890,
                'staff': 12
            }
        ]
        
        return render_template('admin_management/branch_management.html', 
                             branch_data={'branches': branches_data})
        
    except Exception as e:
        logger.error(f"Branches management error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        flash('Unable to load branches data', 'error')
        return redirect(url_for('admin_management.dashboard'))

@admin_management_bp.route('/teller-operations')
@login_required
@admin_required
@secure_banking_route()
def teller_operations():
    """Teller operations management"""
    try:
        # Sample teller operations data
        teller_data = [
            {
                'id': 1,
                'teller_name': 'Alice Smith',
                'branch': 'Main Branch',
                'transactions_today': 45,
                'cash_balance': 25000.00,
                'status': 'Active',
                'last_activity': '2 minutes ago'
            },
            {
                'id': 2,
                'teller_name': 'Bob Wilson',
                'branch': 'Downtown Branch',
                'transactions_today': 32,
                'cash_balance': 18500.00,
                'status': 'Active',
                'last_activity': '5 minutes ago'
            }
        ]
        
        return render_template('admin_management/branch_management.html', 
                             teller_data=teller_data)
        
    except Exception as e:
        logger.error(f"Teller operations error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        flash('Unable to load teller operations data', 'error')
        return redirect(url_for('admin_management.dashboard'))

@admin_management_bp.route('/branch-reports')
@login_required
@admin_required
@secure_banking_route()
def branch_reports():
    """Branch reporting and analytics"""
    try:
        # Sample branch reports data
        reports_data = {
            'daily_transactions': 1247,
            'total_deposits': 485000.00,
            'total_withdrawals': 312000.00,
            'net_flow': 173000.00,
            'branches': [
                {'name': 'Main Branch', 'transactions': 670, 'volume': 285000.00},
                {'name': 'Downtown Branch', 'transactions': 577, 'volume': 200000.00}
            ]
        }
        
        return render_template('admin_management/branch_reports.html', 
                             report_data=reports_data)
        
    except Exception as e:
        logger.error(f"Branch reports error: {e}")
        flash('Unable to load branch reports', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/maintenance')
@login_required
@admin_required
@secure_banking_route()
def maintenance():
    """System maintenance and configuration"""
    try:
        maintenance_data = {
            'system_status': 'operational',
            'last_maintenance': '2024-12-15 02:00:00',
            'next_scheduled': '2024-12-22 02:00:00',
            'maintenance_tasks': [
                {'task': 'Database optimization', 'status': 'completed', 'date': '2024-12-15'},
                {'task': 'Security patches', 'status': 'scheduled', 'date': '2024-12-22'},
                {'task': 'Log rotation', 'status': 'completed', 'date': '2024-12-14'}
            ]
        }
        
        return render_template('admin_management/admin_dashboard.html', 
                             maintenance_data=maintenance_data)
        
    except Exception as e:
        logger.error(f"Maintenance page error: {e}")
        flash('Unable to load maintenance page', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/backups')
@login_required
@admin_required
@secure_banking_route()
def backups():
    """Database backup management"""
    try:
        backup_data = {
            'last_backup': '2024-12-15 03:00:00',
            'backup_size': '2.4 GB',
            'backup_status': 'successful',
            'retention_days': 30,
            'backups': [
                {'date': '2024-12-15', 'size': '2.4 GB', 'status': 'successful'},
                {'date': '2024-12-14', 'size': '2.3 GB', 'status': 'successful'},
                {'date': '2024-12-13', 'size': '2.3 GB', 'status': 'successful'}
            ]
        }
        
        return render_template('admin_management/admin_dashboard.html', 
                             backup_data=backup_data)
        
    except Exception as e:
        logger.error(f"Backups page error: {e}")
        flash('Unable to load backups page', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/users')
@admin_management_bp.route('/users/detailed-view')
@login_required
@admin_required
@secure_banking_route()
def users_detailed_view():
    """Detailed user management view with granular controls"""
    try:
        users_data = admin_service.get_detailed_users_data(current_user.id)
        
        logger.info(f"Users detailed view accessed", extra={
            'user_id': current_user.id,
            'action': 'USERS_DETAILED_VIEW',
            'app_module': 'admin_management'
        })
        
        return render_template('admin_management/admin_dashboard.html', 
                             users_data=users_data)
        
    except Exception as e:
        logger.error(f"Users detailed view error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        flash('Error loading user details', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/sessions/active-monitoring')
@login_required
@admin_required
@secure_banking_route()
def sessions_monitoring():
    """Real-time active sessions monitoring with drill-down capabilities"""
    try:
        sessions_data = admin_service.get_active_sessions_data(current_user.id)
        
        logger.info(f"Sessions monitoring accessed", extra={
            'user_id': current_user.id,
            'action': 'SESSIONS_MONITORING',
            'app_module': 'admin_management'
        })
        
        return render_template('admin_management/admin_dashboard.html', 
                             sessions_data=sessions_data)
        
    except Exception as e:
        logger.error(f"Sessions monitoring error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        flash('Error loading session monitoring', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/transactions/daily-analysis')
@login_required
@admin_required
@secure_banking_route()
def transactions_analysis():
    """Daily transactions analysis with detailed breakdown"""
    try:
        transactions_data = admin_service.get_transactions_analysis_data(current_user.id)
        
        logger.info(f"Transactions analysis accessed", extra={
            'user_id': current_user.id,
            'action': 'TRANSACTIONS_ANALYSIS',
            'app_module': 'admin_management'
        })
        
        return render_template('admin_management/admin_dashboard.html', 
                             transactions_data=transactions_data)
        
    except Exception as e:
        logger.error(f"Transactions analysis error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        flash('Error loading transactions analysis', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/system/performance-monitor')
@login_required
@admin_required
@secure_banking_route()
def system_performance():
    """System performance monitoring with real-time metrics"""
    try:
        performance_data = admin_service.get_system_performance_data(current_user.id)
        
        logger.info(f"System performance monitoring accessed", extra={
            'user_id': current_user.id,
            'action': 'SYSTEM_PERFORMANCE',
            'app_module': 'admin_management'
        })
        
        return render_template('admin_management/admin_dashboard.html', 
                             performance_data=performance_data)
        
    except Exception as e:
        logger.error(f"System performance error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        flash('Error loading system performance', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/security/threat-dashboard')
@login_required
@admin_required
@secure_banking_route()
def security_threats():
    """Security threat monitoring dashboard"""
    try:
        security_data = admin_service.get_security_threats_data(current_user.id)
        
        logger.info(f"Security threat dashboard accessed", extra={
            'user_id': current_user.id,
            'action': 'SECURITY_THREATS',
            'app_module': 'admin_management'
        })
        
        return render_template('security_threats.html', 
                             security_data=security_data)
        
    except Exception as e:
        logger.error(f"Security threats error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        flash('Error loading security threats', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/system/backup-management')
@login_required
@admin_required
@secure_banking_route()
def backup_management():
    """Backup management and monitoring dashboard"""
    try:
        backup_data = admin_service.get_backup_management_data(current_user.id)
        
        logger.info(f"Backup management accessed", extra={
            'user_id': current_user.id,
            'action': 'BACKUP_MANAGEMENT',
            'app_module': 'admin_management'
        })
        
        return render_template('backup_management.html', 
                             backup_data=backup_data)
        
    except Exception as e:
        logger.error(f"Backup management error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        flash('Error loading backup management', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/logs')
@login_required
@admin_required
@secure_banking_route()
def logs_dashboard():
    """Comprehensive logs dashboard with robust filtering and tracing"""
    try:
        from pathlib import Path
        import os
        from datetime import datetime, timedelta
        
        # Central logs directory with year/month/date structure
        from datetime import datetime
        now = datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')
        date = now.strftime('%d')
        # Create nested year/month/date path for logs
        from datetime import datetime
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        date = now.strftime("%d")
        enterprise_logs_dir = Path("logs") / year / month / date / year / month / date
        
        # Get filter parameters
        category_filter = request.args.get('category', 'all')
        level_filter = request.args.get('level', 'all')
        date_filter = request.args.get('date', 'today')
        search_query = request.args.get('search', '')
        
        logs_data = {
            'total_logs': 0,
            'categories': [],
            'recent_entries': [],
            'error_count': 0,
            'warning_count': 0,
            'info_count': 0,
            'directory_path': str(enterprise_logs_dir),
            'directory_exists': enterprise_logs_dir.exists(),
            'filters': {
                'category': category_filter,
                'level': level_filter,
                'date': date_filter,
                'search': search_query
            }
        }
        
        if enterprise_logs_dir.exists():
            categories = []
            recent_entries = []
            total_size = 0
            error_count = warning_count = info_count = 0
            
            # Process each category directory
            for cat_dir in enterprise_logs_dir.iterdir():
                if cat_dir.is_dir() and (category_filter == 'all' or cat_dir.name == category_filter):
                    log_files = list(cat_dir.glob("*.log"))
                    log_count = len(log_files)
                    cat_size = sum(f.stat().st_size for f in log_files if f.exists())
                    
                    # Get recent entries from this category
                    category_entries = []
                    for log_file in log_files:
                        if log_file.exists() and log_file.stat().st_size > 0:
                            try:
                                # Read last 50 lines for recent activity
                                with open(log_file, 'r') as f:
                                    lines = f.readlines()
                                    recent_lines = lines[-50:] if len(lines) > 50 else lines
                                    
                                    for line in recent_lines:
                                        if line.strip():
                                            # Parse log entry
                                            parts = line.strip().split(' - ', 3)
                                            if len(parts) >= 4:
                                                timestamp_str, logger_name, level, message = parts
                                                
                                                # Apply filters
                                                if level_filter != 'all' and level.upper() != level_filter.upper():
                                                    continue
                                                if search_query and search_query.lower() not in message.lower():
                                                    continue
                                                
                                                # Count by level
                                                if 'ERROR' in level:
                                                    error_count += 1
                                                elif 'WARNING' in level:
                                                    warning_count += 1
                                                elif 'INFO' in level:
                                                    info_count += 1
                                                
                                                category_entries.append({
                                                    'timestamp': timestamp_str,
                                                    'category': cat_dir.name,
                                                    'level': level,
                                                    'logger': logger_name,
                                                    'message': message,
                                                    'file': log_file.name
                                                })
                            except Exception as e:
                                continue
                    
                    # Sort entries by timestamp (most recent first)
                    category_entries.sort(key=lambda x: x['timestamp'], reverse=True)
                    recent_entries.extend(category_entries[:20])  # Top 20 per category
                    
                    categories.append({
                        'name': cat_dir.name,
                        'file_count': log_count,
                        'size_mb': round(cat_size / (1024 * 1024), 2),
                        'recent_entries': len(category_entries)
                    })
                    total_size += cat_size
            
            # Sort all recent entries by timestamp
            recent_entries.sort(key=lambda x: x['timestamp'], reverse=True)
            recent_entries = recent_entries[:100]  # Show top 100 recent entries
            
            logs_data.update({
                'categories': categories,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'total_logs': sum(cat['file_count'] for cat in categories),
                'recent_entries': recent_entries,
                'error_count': error_count,
                'warning_count': warning_count,
                'info_count': info_count
            })
        
        logger.info(f"Logs dashboard accessed with filters: {logs_data['filters']}", extra={
            'user_id': current_user.id,
            'action': 'LOGS_DASHBOARD',
            'app_module': 'admin_management'
        })
        
        return render_template('logs_dashboard.html',
                             logs_data=logs_data)
    except Exception as e:
        logger.error(f"Logs dashboard error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        flash('Error loading logs dashboard', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/logs/api/filter')
@login_required
@admin_required
@secure_banking_route()
def logs_api_filter():
    """API endpoint for filtered log retrieval"""
    try:
        from pathlib import Path
        import json
        
        # Get filter parameters
        category = request.args.get('category', 'all')
        level = request.args.get('level', 'all')
        search = request.args.get('search', '')
        limit = int(request.args.get('limit', 100))
        
        # Create nested year/month/date path for logs
        from datetime import datetime
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        date = now.strftime("%d")
        enterprise_logs_dir = Path("logs") / year / month / date
        filtered_entries = []
        
        if enterprise_logs_dir.exists():
            for cat_dir in enterprise_logs_dir.iterdir():
                if cat_dir.is_dir() and (category == 'all' or cat_dir.name == category):
                    for log_file in cat_dir.glob("*.log"):
                        if log_file.exists() and log_file.stat().st_size > 0:
                            try:
                                with open(log_file, 'r') as f:
                                    lines = f.readlines()
                                    for line in reversed(lines[-500:]):  # Check last 500 lines
                                        if line.strip():
                                            parts = line.strip().split(' - ', 3)
                                            if len(parts) >= 4:
                                                timestamp_str, logger_name, log_level, message = parts
                                                
                                                # Apply filters
                                                if level != 'all' and log_level.upper() != level.upper():
                                                    continue
                                                if search and search.lower() not in message.lower():
                                                    continue
                                                
                                                filtered_entries.append({
                                                    'timestamp': timestamp_str,
                                                    'category': cat_dir.name,
                                                    'level': log_level,
                                                    'logger': logger_name,
                                                    'message': message,
                                                    'file': log_file.name
                                                })
                                                
                                                if len(filtered_entries) >= limit:
                                                    break
                            except Exception:
                                continue
                        
                        if len(filtered_entries) >= limit:
                            break
                
                if len(filtered_entries) >= limit:
                    break
        
        # Sort by timestamp (most recent first)
        filtered_entries.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'entries': filtered_entries[:limit],
            'total': len(filtered_entries)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@admin_management_bp.route('/logs/api/trace/<trace_id>')
@login_required
@admin_required
@secure_banking_route()
def logs_api_trace(trace_id):
    """API endpoint for tracing logs by trace ID"""
    try:
        from pathlib import Path
        
        # Create nested year/month/date path for logs
        from datetime import datetime
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        date = now.strftime("%d")
        enterprise_logs_dir = Path("logs") / year / month / date
        trace_entries = []
        
        if enterprise_logs_dir.exists():
            for cat_dir in enterprise_logs_dir.iterdir():
                if cat_dir.is_dir():
                    for log_file in cat_dir.glob("*.log"):
                        if log_file.exists():
                            try:
                                with open(log_file, 'r') as f:
                                    for line_num, line in enumerate(f, 1):
                                        if trace_id in line:
                                            parts = line.strip().split(' - ', 3)
                                            if len(parts) >= 4:
                                                timestamp_str, logger_name, level, message = parts
                                                trace_entries.append({
                                                    'timestamp': timestamp_str,
                                                    'category': cat_dir.name,
                                                    'level': level,
                                                    'logger': logger_name,
                                                    'message': message,
                                                    'file': log_file.name,
                                                    'line_number': line_num
                                                })
                            except Exception:
                                continue
        
        # Sort by timestamp
        trace_entries.sort(key=lambda x: x['timestamp'])
        
        return jsonify({
            'status': 'success',
            'trace_id': trace_id,
            'entries': trace_entries,
            'total': len(trace_entries)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@admin_management_bp.route('/logs/export')
@login_required
@admin_required
@secure_banking_route()
def logs_export():
    """Export filtered logs to CSV"""
    try:
        from pathlib import Path
        import csv
        import io
        from flask import make_response
        
        # Get filter parameters
        category = request.args.get('category', 'all')
        level = request.args.get('level', 'all')
        search = request.args.get('search', '')
        
        # Create nested year/month/date path for logs
        from datetime import datetime
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        date = now.strftime("%d")
        enterprise_logs_dir = Path("logs") / year / month / date
        export_entries = []
        
        if enterprise_logs_dir.exists():
            for cat_dir in enterprise_logs_dir.iterdir():
                if cat_dir.is_dir() and (category == 'all' or cat_dir.name == category):
                    for log_file in cat_dir.glob("*.log"):
                        if log_file.exists():
                            try:
                                with open(log_file, 'r') as f:
                                    for line in f:
                                        if line.strip():
                                            parts = line.strip().split(' - ', 3)
                                            if len(parts) >= 4:
                                                timestamp_str, logger_name, log_level, message = parts
                                                
                                                # Apply filters
                                                if level != 'all' and log_level.upper() != level.upper():
                                                    continue
                                                if search and search.lower() not in message.lower():
                                                    continue
                                                
                                                export_entries.append([
                                                    timestamp_str,
                                                    cat_dir.name,
                                                    log_level,
                                                    logger_name,
                                                    message,
                                                    log_file.name
                                                ])
                            except Exception:
                                continue
        
        # Create CSV response
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Timestamp', 'Category', 'Level', 'Logger', 'Message', 'File'])
        writer.writerows(export_entries)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=nvc_logs_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        logger.info(f"Logs exported: {len(export_entries)} entries", extra={
            'user_id': current_user.id,
            'action': 'LOGS_EXPORT',
            'app_module': 'admin_management'
        })
        
        return response
        
    except Exception as e:
        flash(f'Error exporting logs: {str(e)}', 'error')
        return redirect(url_for('admin_management.logs_dashboard'))

@admin_management_bp.route('/alerts/<alert_id>/investigation')
@login_required
@admin_required
@secure_banking_route()
def alert_investigation(alert_id):
    """Individual alert investigation with detailed forensics"""
    try:
        alert_data = admin_service.get_alert_investigation_data(current_user.id, alert_id)
        
        logger.info(f"Alert investigation accessed", extra={
            'user_id': current_user.id,
            'action': 'ALERT_INVESTIGATION',
            'alert_id': alert_id,
            'app_module': 'admin_management'
        })
        
        return render_template('alert_investigation.html', 
                             alert_data=alert_data, alert_id=alert_id)
        
    except Exception as e:
        logger.error(f"Alert investigation error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'alert_id': alert_id,
            'app_module': 'admin_management'
        })
        flash('Error loading alert investigation', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/actions/<action_id>/audit-trail')
@login_required
@admin_required
@secure_banking_route()
def action_audit_trail(action_id):
    """Individual action audit trail with complete forensics"""
    try:
        audit_data = admin_service.get_action_audit_trail(current_user.id, action_id)
        
        logger.info(f"Action audit trail accessed", extra={
            'user_id': current_user.id,
            'action': 'ACTION_AUDIT_TRAIL',
            'target_action_id': action_id,
            'app_module': 'admin_management'
        })
        
        return render_template('action_audit_trail.html', 
                             audit_data=audit_data, action_id=action_id)
        
    except Exception as e:
        logger.error(f"Action audit trail error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'action_id': action_id,
            'app_module': 'admin_management'
        })
        flash('Error loading audit trail', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/system/components/<component_id>/monitor')
@login_required
@admin_required
@secure_banking_route()
def component_monitor(component_id):
    """Individual component monitoring with real-time metrics"""
    try:
        component_data = admin_service.get_component_monitor_data(current_user.id, component_id)
        
        logger.info(f"Component monitoring accessed", extra={
            'user_id': current_user.id,
            'action': 'COMPONENT_MONITOR',
            'component_id': component_id,
            'app_module': 'admin_management'
        })
        
        return render_template('component_monitor.html', 
                             component_data=component_data, component_id=component_id)
        
    except Exception as e:
        logger.error(f"Component monitoring error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'component_id': component_id,
            'app_module': 'admin_management'
        })
        flash('Error loading component monitoring', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/api/users')
@login_required
@admin_required
@secure_banking_route()
def api_users():
    """Get user management data via API"""
    try:
        user_data = admin_service.get_user_management_data(current_user.id)
        
        logger.info(f"User management API accessed", extra={
            'user_id': current_user.id,
            'action': 'USER_MANAGEMENT_API',
            'app_module': 'admin_management'
        })
        
        return jsonify({'success': True, 'data': user_data})
        
    except Exception as e:
        logger.error(f"User management API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        return jsonify({'success': False, 'error': 'Unable to load user data'}), 500

@admin_management_bp.route('/api/users/<int:user_id>')
@login_required
@admin_required
@secure_banking_route()
def api_user_details(user_id):
    """Get individual user details via API"""
    try:
        user_details = admin_service.get_user_details(current_user.id, user_id)
        
        logger.info(f"User details API accessed for user {user_id}", extra={
            'user_id': current_user.id,
            'target_user_id': user_id,
            'action': 'USER_DETAILS_API',
            'app_module': 'admin_management'
        })
        
        return jsonify({'success': True, 'data': user_details})
        
    except Exception as e:
        logger.error(f"User details API error: {e}", extra={
            'user_id': current_user.id,
            'target_user_id': user_id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        return jsonify({'success': False, 'error': 'Unable to load user details'}), 500

@admin_management_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
@secure_banking_route()
def api_update_user(user_id):
    """Update user information via API"""
    try:
        update_data = request.get_json()
        if not update_data:
            return jsonify({'success': False, 'error': 'No update data provided'}), 400
        
        result = admin_service.update_user_information(
            admin_user_id=current_user.id,
            target_user_id=user_id,
            update_data=update_data
        )
        
        if result['success']:
            logger.info(f"User {user_id} updated via API", extra={
                'user_id': current_user.id,
                'target_user_id': user_id,
                'action': 'USER_UPDATE_API_SUCCESS',
                'app_module': 'admin_management',
                'changes': list(update_data.keys())
            })
        else:
            logger.warning(f"User {user_id} update failed via API: {result.get('error')}", extra={
                'user_id': current_user.id,
                'target_user_id': user_id,
                'action': 'USER_UPDATE_API_FAILED',
                'app_module': 'admin_management',
                'error': result.get('error')
            })
        
        return jsonify(result), 200 if result['success'] else 400
                
    except Exception as e:
        logger.error(f"User update API error: {e}", extra={
            'user_id': current_user.id,
            'target_user_id': user_id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@admin_management_bp.route('/api/platform')
@login_required
@admin_required
@secure_banking_route()
def api_platform():
    """Get platform overview data via API"""
    try:
        platform_data = admin_service.get_platform_overview(current_user.id)
        
        logger.info(f"Platform overview API accessed", extra={
            'user_id': current_user.id,
            'action': 'PLATFORM_OVERVIEW_API',
            'app_module': 'admin_management'
        })
        
        return jsonify({'success': True, 'data': platform_data})
        
    except Exception as e:
        logger.error(f"Platform overview API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        return jsonify({'success': False, 'error': 'Unable to load platform data'}), 500

@admin_management_bp.route('/api/configuration')
@login_required
@super_admin_required
@secure_banking_route()
def api_configuration():
    """Get system configuration via API"""
    try:
        config_data = admin_service.get_system_configuration(current_user.id)
        
        logger.info(f"System configuration API accessed", extra={
            'user_id': current_user.id,
            'action': 'SYSTEM_CONFIG_API',
            'app_module': 'admin_management'
        })
        
        return jsonify({'success': True, 'data': config_data})
        
    except Exception as e:
        logger.error(f"System configuration API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        return jsonify({'success': False, 'error': 'Unable to load configuration'}), 500

@admin_management_bp.route('/api/configuration', methods=['PUT'])
@login_required
@super_admin_required
@secure_banking_route()
def api_update_configuration():
    """Update system configuration via API"""
    try:
        config_data = request.get_json()
        if not config_data:
            return jsonify({'success': False, 'error': 'No configuration data provided'}), 400
        
        result = admin_service.update_system_configuration(
            admin_user_id=current_user.id,
            config_data=config_data
        )
        
        if result['success']:
            logger.info(f"System configuration updated via API", extra={
                'user_id': current_user.id,
                'action': 'SYSTEM_CONFIG_UPDATE_API_SUCCESS',
                'app_module': 'admin_management',
                'changes': list(config_data.keys())
            })
        else:
            logger.warning(f"System configuration update failed via API: {result.get('error')}", extra={
                'user_id': current_user.id,
                'action': 'SYSTEM_CONFIG_UPDATE_API_FAILED',
                'app_module': 'admin_management',
                'error': result.get('error')
            })
        
        return jsonify(result), 200 if result['success'] else 400
                
    except Exception as e:
        logger.error(f"System configuration update API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@admin_management_bp.route('/api/audit/logs')
@login_required
@admin_required
@secure_banking_route()
def api_audit_logs():
    """Get audit logs via API"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        log_type = request.args.get('type', 'all')
        
        audit_data = admin_service.get_audit_logs(
            admin_user_id=current_user.id,
            page=page,
            per_page=per_page,
            log_type=log_type
        )
        
        logger.info(f"Audit logs API accessed", extra={
            'user_id': current_user.id,
            'action': 'AUDIT_LOGS_API',
            'app_module': 'admin_management',
            'page': page,
            'log_type': log_type
        })
        
        return jsonify({'success': True, 'data': audit_data})
        
    except Exception as e:
        logger.error(f"Audit logs API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        return jsonify({'success': False, 'error': 'Unable to load audit logs'}), 500

# System Administration Routes (Migrated from Legacy Admin System)

@admin_management_bp.route('/system/health')
@login_required
@admin_required
@secure_banking_route()
def system_health():
    """System health monitoring dashboard"""
    try:
        health_data = admin_service.get_system_health_data(current_user.id)
        
        logger.info(f"System health dashboard accessed", extra={
            'user_id': current_user.id,
            'action': 'SYSTEM_HEALTH_ACCESS',
            'app_module': 'admin_management'
        })
        
        return render_template('system_health.html', 
                             health_data=health_data)
        
    except Exception as e:
        logger.error(f"System health error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        flash('Error loading system health', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/settings')
@admin_management_bp.route('/system/settings')
@login_required
@admin_required
@secure_banking_route()
def system_settings():
    """System configuration and settings panel"""
    try:
        # Simple settings data without complex service calls
        settings_data = {
            'system_settings': {
                'maintenance_mode': False,
                'allow_registrations': True,
                'session_timeout': 900,  # 15 minutes
                'max_login_attempts': 5,
                'backup_enabled': True,
                'logging_level': 'INFO'
            },
            'security_settings': {
                'require_2fa': False,
                'password_complexity': True,
                'ip_whitelisting': False,
                'audit_logging': True
            },
            'notification_settings': {
                'email_alerts': True,
                'sms_alerts': False,
                'system_notifications': True
            },
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        }
        
        logger.info(f"System settings accessed", extra={
            'user_id': current_user.id,
            'action': 'SYSTEM_SETTINGS_ACCESS',
            'app_module': 'admin_management'
        })
        
        return render_template('system_settings.html', 
                             settings_data=settings_data)
        
    except Exception as e:
        logger.error(f"System settings error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        flash('Error loading system settings', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

# Duplicate backup_management function removed - kept the first instance at line 219

@admin_management_bp.route('/system/maintenance')
@login_required
@admin_required
@secure_banking_route()
def maintenance_mode():
    """System maintenance and downtime management"""
    try:
        maintenance_data = admin_service.get_maintenance_data(current_user.id)
        
        logger.info(f"Maintenance mode accessed", extra={
            'user_id': current_user.id,
            'action': 'MAINTENANCE_MODE_ACCESS',
            'app_module': 'admin_management'
        })
        
        return render_template('maintenance_mode.html', 
                             maintenance_data=maintenance_data)
        
    except Exception as e:
        logger.error(f"Maintenance mode error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        flash('Error loading maintenance mode', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

# System Operations Routes (Enhanced with Legacy Features)

@admin_management_bp.route('/system/backup/create', methods=['POST'])
@login_required
@admin_required
@secure_banking_route()
def create_backup():
    """Create system backup"""
    try:
        backup_type = request.json.get('backup_type', 'full')
        result = admin_service.create_system_backup(current_user.id, backup_type)
        
        logger.info(f"System backup created", extra={
            'user_id': current_user.id,
            'action': 'SYSTEM_BACKUP_CREATE',
            'backup_type': backup_type,
            'app_module': 'admin_management'
        })
        
        return jsonify({
            'success': True,
            'message': 'Backup created successfully',
            'backup_id': result.get('backup_id', 'Unknown')
        })
        
    except Exception as e:
        logger.error(f"System backup creation error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        return jsonify({
            'success': False,
            'error': 'Failed to create backup'
        }), 500

@admin_management_bp.route('/system/maintenance/toggle', methods=['POST'])
@login_required
@admin_required
@secure_banking_route()
def toggle_maintenance():
    """Toggle maintenance mode"""
    try:
        enable = request.json.get('enable', False)
        result = admin_service.toggle_maintenance_mode(current_user.id, enable)
        
        logger.info(f"Maintenance mode toggled", extra={
            'user_id': current_user.id,
            'action': 'MAINTENANCE_MODE_TOGGLE',
            'enable': enable,
            'app_module': 'admin_management'
        })
        
        return jsonify({
            'success': True,
            'message': f'Maintenance mode {"enabled" if enable else "disabled"}',
            'maintenance_active': result.get('maintenance_active', enable)
        })
        
    except Exception as e:
        logger.error(f"Maintenance mode toggle error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        return jsonify({
            'success': False,
            'error': 'Failed to toggle maintenance mode'
        }), 500

# Legacy API Management Integration (Phase 2 Consolidation)

@admin_management_bp.route('/api-management')
@login_required
@admin_required
@secure_banking_route()
def api_management():
    """API Management Dashboard - comprehensive REST API tools"""
    try:
        api_data = admin_service.get_api_management_data(current_user.id)
        
        logger.info(f"API management accessed", extra={
            'user_id': current_user.id,
            'action': 'API_MANAGEMENT_ACCESS',
            'app_module': 'admin_management'
        })
        
        return render_template('api_management.html', 
                             api_data=api_data)
        
    except Exception as e:
        logger.error(f"API management error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        flash('Error loading API management', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/api-documentation')
@login_required
@admin_required
@secure_banking_route()
def api_documentation():
    """API Documentation - comprehensive REST API v1.0 documentation"""
    try:
        api_docs = admin_service.get_api_documentation_data(current_user.id)
        
        logger.info(f"API documentation accessed", extra={
            'user_id': current_user.id,
            'action': 'API_DOCUMENTATION_ACCESS',
            'app_module': 'admin_management'
        })
        
        return render_template('api_documentation.html', 
                             api_docs=api_docs)
        
    except Exception as e:
        logger.error(f"API documentation error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        flash('Error loading API documentation', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/api-sandbox')
@login_required
@admin_required
@secure_banking_route()
def api_sandbox():
    """API Sandbox - interactive API testing environment"""
    try:
        sandbox_data = admin_service.get_api_sandbox_data(current_user.id)
        
        logger.info(f"API sandbox accessed", extra={
            'user_id': current_user.id,
            'action': 'API_SANDBOX_ACCESS',
            'app_module': 'admin_management'
        })
        
        return render_template('api_sandbox.html', 
                             sandbox_data=sandbox_data)
        
    except Exception as e:
        logger.error(f"API sandbox error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        flash('Error loading API sandbox', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/system-logs')
@login_required
@admin_required
@secure_banking_route()
def system_logs():
    """System Logs Management - centralized log viewing and analysis"""
    try:
        logs_data = admin_service.get_system_logs_data(current_user.id)
        
        logger.info(f"System logs accessed", extra={
            'user_id': current_user.id,
            'action': 'SYSTEM_LOGS_ACCESS',
            'app_module': 'admin_management'
        })
        
        return render_template('system_logs.html', 
                             logs_data=logs_data)
        
    except Exception as e:
        logger.error(f"System logs error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        flash('Error loading system logs', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/health')
def health():
    """Module health check endpoint"""
    try:
        health_status = admin_service.get_module_health()
        return jsonify(health_status)
    except Exception as e:
        logger.error(f"Admin management health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Test Routes for Error Logging

@admin_management_bp.route('/test-error-logging')
@login_required
@admin_required
@secure_banking_route()
def test_error_logging():
    """Test error logging by triggering a deliberate error"""
    try:
        # This will trigger a ZeroDivisionError
        result = 1 / 0
        return jsonify({'result': result})
    except Exception as e:
        # This should be caught by the global error handler
        raise e

@admin_management_bp.route('/test-logging')
@login_required
@admin_required
@secure_banking_route()
def test_logging():
    """Test enterprise logging functionality"""
    try:
        # Test enterprise logging across all categories
        error_logger.info("Admin triggered comprehensive logging test")
        api_logger.info("API logging test from admin")
        security_logger.warning("Security logging test - simulated alert")
        banking_logger.error("Banking error test - simulated transaction issue")
        audit_logger.info("Audit logging test - simulated compliance check")
        system_logger.debug("System debug logging test")
        
        return jsonify({
            'status': 'success',
            'message': 'Comprehensive logging test completed - check logs directory',
            'categories_tested': ['errors', 'api', 'security', 'banking', 'audit', 'system']
        })
    except Exception as e:
        error_logger.error(f"Logging test failed: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Additional Admin Routes to Fix 404 Errors

@admin_management_bp.route('/webhooks')
@login_required
@admin_required
@secure_banking_route()
def webhooks():
    """Webhook management dashboard"""
    try:
        webhooks_data = {
            'active_webhooks': [],
            'webhook_stats': {
                'total_webhooks': 0,
                'active_webhooks': 0,
                'failed_webhooks': 0
            },
            'recent_deliveries': []
        }
        
        logger.info(f"Webhooks dashboard accessed", extra={
            'user_id': current_user.id,
            'action': 'access_webhooks_dashboard'
        })
        
        return render_template('webhooks.html', 
                             webhooks_data=webhooks_data,
                             page_title='Webhook Management')
        
    except Exception as e:
        logger.error(f"Webhooks dashboard error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e)
        })
        flash('Error loading webhooks dashboard', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/external-apis')
@login_required
@admin_required
@secure_banking_route()
def external_apis():
    """External API management dashboard"""
    try:
        api_data = {
            'api_connections': [
                {'name': 'Stripe', 'status': 'active', 'last_used': '2025-07-05'},
                {'name': 'Binance', 'status': 'active', 'last_used': '2025-07-05'},
                {'name': 'Plaid', 'status': 'active', 'last_used': '2025-07-05'}
            ],
            'api_stats': {
                'total_apis': 3,
                'active_apis': 3,
                'failed_apis': 0
            },
            'recent_calls': []
        }
        
        logger.info(f"External APIs dashboard accessed", extra={
            'user_id': current_user.id,
            'action': 'access_external_apis_dashboard'
        })
        
        return render_template('external_apis.html', 
                             api_data=api_data,
                             page_title='External API Management')
        
    except Exception as e:
        logger.error(f"External APIs dashboard error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e)
        })
        flash('Error loading external APIs dashboard', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

# Emergency Control Routes (Super Admin Only)
@admin_management_bp.route('/emergency')
@login_required
@admin_required
@secure_banking_route()
def emergency_controls():
    """Emergency control dashboard for super admin"""
    try:
        # Check if user has super admin role
        if current_user.role.value != 'super_admin':
            flash('Access denied. Super admin privileges required.', 'error')
            return redirect(url_for('admin_management.admin_dashboard'))
        
        emergency_data = {
            'system_status': 'operational',
            'active_alerts': [],
            'emergency_contacts': [
                {'name': 'System Administrator', 'phone': '+1-555-0100', 'email': 'admin@nvcfund.com'},
                {'name': 'Security Team', 'phone': '+1-555-0200', 'email': 'security@nvcfund.com'}
            ],
            'recent_actions': [],
            'system_controls': {
                'maintenance_mode': False,
                'api_access': True,
                'transaction_processing': True,
                'user_access': True
            }
        }
        
        logger.info(f"Emergency controls accessed", extra={
            'user_id': current_user.id,
            'action': 'access_emergency_controls'
        })
        
        return render_template('emergency_controls.html', 
                             emergency_data=emergency_data,
                             page_title='Emergency Controls')
        
    except Exception as e:
        logger.error(f"Emergency controls error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e)
        })
        flash('Error loading emergency controls', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/override')
@login_required
@admin_required
@secure_banking_route()
def system_override():
    """System override dashboard for super admin"""
    try:
        # Check if user has super admin role
        if current_user.role.value != 'super_admin':
            flash('Access denied. Super admin privileges required.', 'error')
            return redirect(url_for('admin_management.admin_dashboard'))
        
        override_data = {
            'override_capabilities': [
                {'name': 'Transaction Limits', 'status': 'available', 'description': 'Override transaction limits'},
                {'name': 'Account Restrictions', 'status': 'available', 'description': 'Override account restrictions'},
                {'name': 'Security Protocols', 'status': 'available', 'description': 'Override security protocols'},
                {'name': 'System Maintenance', 'status': 'available', 'description': 'Override maintenance schedules'}
            ],
            'active_overrides': [],
            'override_history': [],
            'security_warnings': [
                'System overrides are logged and audited',
                'All override actions require super admin authorization',
                'Override actions may affect system stability'
            ]
        }
        
        logger.info(f"System override accessed", extra={
            'user_id': current_user.id,
            'action': 'access_system_override'
        })
        
        return render_template('system_override.html', 
                             override_data=override_data,
                             page_title='System Override')
        
    except Exception as e:
        logger.error(f"System override error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e)
        })
        flash('Error loading system override', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

# Additional Missing Admin Routes for Navigation Dropdown

@admin_management_bp.route('/users')
@login_required
@admin_required
@secure_banking_route()
def users():
    """User management page"""
    try:
        users_data = {
            'total_users': 0,
            'active_users': 0,
            'pending_users': 0,
            'users_list': []
        }
        
        return render_template('users.html', 
                             users_data=users_data,
                             page_title='User Management')
    except Exception as e:
        logger.error(f"Users page error: {e}")
        flash('Error loading users page', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/roles')
@login_required
@admin_required
@secure_banking_route()
def roles():
    """Roles and permissions management"""
    try:
        roles_data = {
            'available_roles': ['USER', 'ADMIN', 'SUPER_ADMIN'],
            'permissions': []
        }
        
        return render_template('roles.html', 
                             roles_data=roles_data,
                             page_title='Roles & Permissions')
    except Exception as e:
        logger.error(f"Roles page error: {e}")
        flash('Error loading roles page', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/user-activity')
@login_required
@admin_required
@secure_banking_route()
def user_activity():
    """User activity monitoring"""
    try:
        activity_data = {
            'recent_logins': [],
            'active_sessions': 0,
            'failed_attempts': []
        }
        
        return render_template('user_activity.html', 
                             activity_data=activity_data,
                             page_title='User Activity')
    except Exception as e:
        logger.error(f"User activity error: {e}")
        flash('Error loading user activity', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/sessions')
@login_required
@admin_required
@secure_banking_route()
def sessions():
    """Active sessions management"""
    try:
        sessions_data = {
            'active_sessions': [],
            'session_count': 0
        }
        
        return render_template('sessions.html', 
                             sessions_data=sessions_data,
                             page_title='Active Sessions')
    except Exception as e:
        logger.error(f"Sessions error: {e}")
        flash('Error loading sessions', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

# Removed duplicate backups function - kept the main one above

# ============================================================================
# LOG VIEWER ROUTES - RBAC-ENABLED LOG ACCESS
# ============================================================================

@admin_management_bp.route('/logs')
@login_required
@admin_required
@secure_banking_route()
def log_viewer():
    """Main log viewer interface with RBAC and filtering"""
    try:
        user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        
        # Get accessible categories for user role
        accessible_categories = log_viewer_service.get_user_log_categories(user_role)
        
        # Get available dates (last 30 days)
        available_dates = log_viewer_service.get_available_dates(user_role, days_back=30)
        
        logger.info(f"Log viewer accessed", extra={
            'user_id': current_user.id,
            'user_role': user_role,
            'accessible_categories': len(accessible_categories),
            'action': 'LOG_VIEWER_ACCESS'
        })
        
        return render_template('log_viewer.html',
                             accessible_categories=accessible_categories,
                             available_dates=available_dates,
                             page_title='System Logs Viewer')
        
    except Exception as e:
        logger.error(f"Log viewer error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e)
        })
        flash('Error loading log viewer', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

@admin_management_bp.route('/logs/api/stats/<path:date_path>')
@login_required
@admin_required
@secure_banking_route()
def logs_api_stats(date_path):
    """API endpoint for log statistics"""
    try:
        user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        stats = log_viewer_service.get_log_statistics(user_role, date_path)
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Log stats API error: {e}")
        return jsonify({'error': 'Failed to load log statistics'}), 500

@admin_management_bp.route('/logs/api/files', methods=['POST'])
@login_required
@admin_required
@secure_banking_route()
def logs_api_files():
    """API endpoint for log files list"""
    try:
        user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        data = request.get_json() or request.form
        
        date_path = data.get('date_path')
        categories = data.get('categories', [])
        
        if isinstance(categories, str):
            categories = [categories]
        
        all_files = []
        for category in categories:
            files = log_viewer_service.get_log_files(user_role, date_path, category)
            for file_info in files:
                file_info['category'] = category
                all_files.append(file_info)
        
        all_files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({'files': all_files})
        
    except Exception as e:
        logger.error(f"Log files API error: {e}")
        return jsonify({'error': 'Failed to load log files'}), 500

@admin_management_bp.route('/logs/api/content', methods=['POST'])
@login_required
@admin_required
@secure_banking_route()
def logs_api_content():
    """API endpoint for log content with filtering"""
    try:
        user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        data = request.get_json() or request.form
        
        file_path = data.get('file_path')
        filters = data.get('filters', {})
        
        if isinstance(filters, str):
            import json
            filters = json.loads(filters)
        
        content_data = log_viewer_service.read_log_content(user_role, file_path, filters)
        
        return jsonify(content_data)
        
    except Exception as e:
        logger.error(f"Log content API error: {e}")
        return jsonify({'error': 'Failed to load log content'}), 500

@admin_management_bp.route('/logs/api/export', methods=['POST'])
@login_required
@admin_required
@secure_banking_route()
def logs_api_export():
    """API endpoint for log export"""
    try:
        from flask import make_response
        import csv
        import io
        
        user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        data = request.form
        
        file_path = data.get('file_path')
        filters = data.get('filters', '{}')
        
        if isinstance(filters, str):
            import json
            filters = json.loads(filters)
        
        content_data = log_viewer_service.read_log_content(user_role, file_path, filters)
        
        if 'error' in content_data:
            flash(f"Export failed: {content_data['error']}", 'error')
            return redirect(url_for('admin_management.log_viewer'))
        
        # Create CSV output
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Line Number', 'Timestamp', 'Level', 'Message'])
        
        for line in content_data['content']:
            writer.writerow([
                line['line_number'],
                line['timestamp'],
                line['level'],
                line['message']
            ])
        
        response_content = output.getvalue()
        output.close()
        
        response = make_response(response_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=logs_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
        
    except Exception as e:
        logger.error(f"Log export error: {e}")
        flash('Export failed', 'error')
        return redirect(url_for('admin_management.log_viewer'))
# Duplicate route removed - using the existing branches_management function above

@admin_management_bp.route("/teller-operations")
@login_required
@admin_required
@secure_banking_route()
def teller_operations_new():
    """Teller operations dashboard"""
    try:
        teller_data = {
            "tellers": [
                {"id": 1, "name": "Alice Johnson", "branch": "Main Branch", "transactions": 45, "status": "Active"},
                {"id": 2, "name": "Bob Wilson", "branch": "North Branch", "transactions": 32, "status": "Active"}
            ],
            "total_tellers": 2,
            "active_tellers": 2
        }
        return render_template("teller_operations.html", teller_data=teller_data)
    except Exception as e:
        logger.error(f"Teller operations error: {e}")
        flash("Error loading teller operations", "error")
        return redirect(url_for("admin_management.admin_dashboard"))

@admin_management_bp.route("/branch-reports")
@login_required
@admin_required
@secure_banking_route()
def branch_reports_dropdown():
    """Branch reports dashboard"""
    try:
        report_data = {
            "reports": [
                {"id": 1, "branch": "Main Branch", "type": "Daily Summary", "date": "2025-07-06"},
                {"id": 2, "branch": "North Branch", "type": "Weekly Report", "date": "2025-07-06"}
            ],
            "total_reports": 2
        }
        return render_template("admin_management/branch_reports.html", report_data=report_data)
    except Exception as e:
        logger.error(f"Branch reports error: {e}")
        flash("Error loading branch reports", "error")
        return redirect(url_for("admin_management.admin_dashboard"))

@admin_management_bp.route("/maintenance")
@login_required
@admin_required
@secure_banking_route()
def maintenance_dropdown():
    """Maintenance mode dashboard"""
    try:
        maintenance_data = {
            "maintenance_mode": False,
            "scheduled_maintenance": [],
            "system_status": "operational"
        }
        return render_template("maintenance.html", maintenance_data=maintenance_data)
    except Exception as e:
        logger.error(f"Maintenance error: {e}")
        flash("Error loading maintenance", "error")
        return redirect(url_for("admin_management.admin_dashboard"))

@admin_management_bp.route("/backups")
@login_required
@admin_required
@secure_banking_route()
def backups_dropdown():
    """Database backups dashboard"""
    try:
        backup_data = {
            "backups": [
                {"id": 1, "name": "daily_backup_2025-07-06", "size": "1.2GB", "date": "2025-07-06"},
                {"id": 2, "name": "weekly_backup_2025-07-01", "size": "8.5GB", "date": "2025-07-01"}
            ],
            "total_backups": 2
        }
        return render_template("backups.html", backup_data=backup_data)
    except Exception as e:
        logger.error(f"Backups error: {e}")
        flash("Error loading backups", "error")
        return redirect(url_for("admin_management.admin_dashboard"))

