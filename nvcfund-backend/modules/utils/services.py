"""
Utils Module Services - Self-contained utility services
Provides navbar context and error logging services
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Any
from flask_login import current_user

class NavbarContextService:
    """
    Self-contained navbar context service
    Provides consistent navbar structure for all templates
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_navbar_context(self) -> Dict[str, Any]:
        """
        Generate complete navbar context for templates
        Returns a properly structured context that templates expect
        """
        try:
            # Base navigation items that all users see
            base_navigation = {
                'dashboard': {
                    'title': 'Dashboard',
                    'icon': 'fas fa-tachometer-alt',
                    'items': self._get_dashboard_items
                },
                'help_support': {
                    'title': 'Help & Support', 
                    'icon': 'fas fa-life-ring',
                    'items': self._get_help_support_items
                }
            }
            
            # User-specific navigation based on role
            user_navigation = self._get_user_navigation()
            
            return {
                'base_navigation': base_navigation,
                'user_navigation': user_navigation,
                'current_user': current_user if current_user.is_authenticated else None
            }
            
        except Exception as e:
            self.logger.error(f"Error generating navbar context: {e}")
            return self._get_fallback_context()
    
    def _get_dashboard_items(self) -> List[Dict[str, str]]:
        """Get dashboard dropdown items"""
        return [
            {'title': 'Main Dashboard', 'route': '/dashboard/', 'icon': 'fas fa-home'},
            {'title': 'Overview', 'route': '/dashboard/overview', 'icon': 'fas fa-chart-line'},
            {'title': 'Quick Actions', 'route': '/dashboard/quick-actions', 'icon': 'fas fa-bolt'},
            {'title': 'Recent Activity', 'route': '/dashboard/recent-activity', 'icon': 'fas fa-history'}
        ]
    
    def _get_help_support_items(self) -> List[Dict[str, str]]:
        """Get help & support dropdown items"""
        return [
            {'title': 'Documentation', 'route': '/documentation', 'icon': 'fas fa-book'},
            {'title': 'Contact Support', 'route': '/contact', 'icon': 'fas fa-envelope'},
            {'title': 'FAQ', 'route': '/faq', 'icon': 'fas fa-question-circle'},
            {'title': 'Live Chat', 'route': '/chat/', 'icon': 'fas fa-comments'}
        ]
    
    def _get_user_navigation(self) -> Dict[str, Any]:
        """Get user-specific navigation based on role"""
        if not current_user.is_authenticated:
            return {}
            
        user_role = getattr(current_user, 'role', None)
        if user_role and hasattr(user_role, 'value'):
            role_value = user_role.value
        else:
            role_value = 'standard'
            
        # Standard user navigation
        if role_value in ['standard', 'user']:
            return {
                'banking': {
                    'title': 'Banking',
                    'icon': 'fas fa-university',
                    'items': self._get_standard_banking_items
                },
                'services': {
                    'title': 'Services',
                    'icon': 'fas fa-cogs',
                    'items': self._get_standard_services_items
                }
            }
        
        # Admin user navigation
        elif role_value in ['admin', 'super_admin']:
            return {
                'admin': {
                    'title': 'Admin',
                    'icon': 'fas fa-shield-alt',
                    'items': self._get_admin_items
                },
                'system': {
                    'title': 'System',
                    'icon': 'fas fa-server',
                    'items': self._get_system_items
                }
            }
        
        # Treasury user navigation
        elif role_value in ['treasury_officer', 'treasury']:
            return {
                'treasury': {
                    'title': 'Treasury',
                    'icon': 'fas fa-coins',
                    'items': self._get_treasury_items
                }
            }
        
        # Sovereign banking user navigation
        elif role_value in ['central_bank_governor', 'sovereign_banker', 'monetary_policy_committee']:
            return {
                'sovereign': {
                    'title': 'Sovereign Banking',
                    'icon': 'fas fa-university',
                    'items': self._get_sovereign_items
                }
            }
        
        # Default fallback
        return self._get_default_navigation()
    
    
    def _get_tier_one_navigation_items(self) -> List[Dict[str, str]]:
        """Tier one features navigation items"""
        return [
            {'title': 'Accounts', 'route': '/accounts/', 'icon': 'fas fa-university'},
            {'title': 'Treasury', 'route': '/treasury/', 'icon': 'fas fa-coins'},
            {'title': 'Settlement', 'route': '/settlement/', 'icon': 'fas fa-handshake'},
            {'title': 'Compliance', 'route': '/compliance/', 'icon': 'fas fa-shield-alt'},
            {'title': 'Institutional', 'route': '/institutional/', 'icon': 'fas fa-building'},
            {'title': 'Cards & Payments', 'route': '/cards_payments/', 'icon': 'fas fa-credit-card'},
            {'title': 'Investments', 'route': '/investments/', 'icon': 'fas fa-chart-line'},
            {'title': 'Insurance', 'route': '/insurance/', 'icon': 'fas fa-umbrella'}
        ]

    def _get_standard_banking_items(self) -> List[Dict[str, str]]:
        """Standard banking items for regular users"""
        return [
            {'title': 'Banking Dashboard', 'route': '/banking/', 'icon': 'fas fa-tachometer-alt'},
            {'title': 'Account Management', 'route': '/banking/accounts', 'icon': 'fas fa-wallet'},
            {'title': 'Money Transfers', 'route': '/banking/transfers', 'icon': 'fas fa-exchange-alt'},
            {'title': 'Payment Cards', 'route': '/banking/cards', 'icon': 'fas fa-credit-card'},
            {'title': 'Bill Payments', 'route': '/banking/payments', 'icon': 'fas fa-money-bill-wave'},
            {'title': 'Transaction History', 'route': '/banking/history', 'icon': 'fas fa-history'},
            {'title': 'Account Statements', 'route': '/banking/statements', 'icon': 'fas fa-file-alt'},
            {'title': 'Security Settings', 'route': '/banking/security', 'icon': 'fas fa-shield-alt'}
        ]
    
    def _get_standard_services_items(self) -> List[Dict[str, str]]:
        """Standard services items for regular users"""
        return [
            {'title': 'Bill Pay', 'route': '/services/bill-pay', 'icon': 'fas fa-file-invoice-dollar'},
            {'title': 'Loans', 'route': '/services/loans', 'icon': 'fas fa-hand-holding-usd'},
            {'title': 'Investment', 'route': '/services/investment', 'icon': 'fas fa-chart-line'},
            {'title': 'Insurance', 'route': '/services/insurance', 'icon': 'fas fa-shield-alt'}
        ]
    
    def _get_admin_items(self) -> List[Dict[str, str]]:
        """Admin navigation items - privileged services"""
        return [
            {'title': 'Admin Dashboard', 'route': '/admin/dashboard', 'icon': 'fas fa-tachometer-alt'},
            {'title': 'User Management', 'route': '/admin/users', 'icon': 'fas fa-users'},
            {'title': 'Security Center', 'route': '/security/dashboard', 'icon': 'fas fa-shield-alt'},
            {'title': 'System Management', 'route': '/system/dashboard', 'icon': 'fas fa-server'},
            {'title': 'Analytics', 'route': '/analytics/dashboard', 'icon': 'fas fa-chart-line'},
            {'title': 'Treasury Operations', 'route': '/treasury/dashboard', 'icon': 'fas fa-coins'},
            {'title': 'Compliance', 'route': '/compliance/dashboard', 'icon': 'fas fa-balance-scale'},
            {'title': 'Settlement', 'route': '/settlement/dashboard', 'icon': 'fas fa-handshake'},
            {'title': 'Reports', 'route': '/admin/reports', 'icon': 'fas fa-chart-bar'}
        ]
    
    def _get_system_items(self) -> List[Dict[str, str]]:
        """System navigation items"""
        return [
            {'title': 'System Health', 'route': '/admin/system/health', 'icon': 'fas fa-heartbeat'},
            {'title': 'Logs', 'route': '/admin/logs', 'icon': 'fas fa-file-alt'},
            {'title': 'Settings', 'route': '/admin/settings', 'icon': 'fas fa-cog'},
            {'title': 'Monitoring', 'route': '/admin/system/monitoring', 'icon': 'fas fa-eye'}
        ]
    
    def _get_treasury_items(self) -> List[Dict[str, str]]:
        """Treasury navigation items"""
        return [
            {'title': 'NVCT Stablecoin', 'route': '/nvct/', 'icon': 'fas fa-coins'},
            {'title': 'Supply Management', 'route': '/nvct/supply', 'icon': 'fas fa-cogs'},
            {'title': 'Asset Backing', 'route': '/nvct/assets', 'icon': 'fas fa-vault'},
            {'title': 'Network Management', 'route': '/nvct/networks', 'icon': 'fas fa-network-wired'},
            {'title': 'Cross-Chain Bridge', 'route': '/nvct/bridge', 'icon': 'fas fa-exchange-alt'},
            {'title': 'Governance', 'route': '/nvct/governance', 'icon': 'fas fa-vote-yea'},
            {'title': 'Analytics', 'route': '/nvct/analytics', 'icon': 'fas fa-chart-line'},
            {'title': 'Treasury Reports', 'route': '/treasury/reports', 'icon': 'fas fa-file-alt'}
        ]
    
    def _get_sovereign_items(self) -> List[Dict[str, str]]:
        """Sovereign banking navigation items"""
        return [
            {'title': 'Central Banking', 'route': '/sovereign/central-bank', 'icon': 'fas fa-university'},
            {'title': 'Monetary Policy', 'route': '/sovereign/monetary-policy', 'icon': 'fas fa-percentage'},
            {'title': 'Sovereign Debt', 'route': '/sovereign/sovereign-debt', 'icon': 'fas fa-chart-pie'},
            {'title': 'Foreign Exchange', 'route': '/sovereign/foreign-exchange', 'icon': 'fas fa-exchange-alt'},
            {'title': 'International Reserves', 'route': '/sovereign/reserves', 'icon': 'fas fa-coins'},
            {'title': 'Banking Regulation', 'route': '/sovereign/regulatory', 'icon': 'fas fa-shield-alt'}
        ]
    
    def _get_default_navigation(self) -> Dict[str, Any]:
        """Default navigation for unknown roles"""
        return {
            'general': {
                'title': 'Services',
                'icon': 'fas fa-cogs',
                'items': lambda: [
                    {'title': 'Account', 'route': '/account', 'icon': 'fas fa-user'},
                    {'title': 'Settings', 'route': '/settings', 'icon': 'fas fa-cog'}
                ]
            }
        }
    
    def _get_fallback_context(self) -> Dict[str, Any]:
        """Fallback context when errors occur"""
        return {
            'base_navigation': {
                'dashboard': {
                    'title': 'Dashboard',
                    'icon': 'fas fa-tachometer-alt',
                    'items': lambda: []
                },
                'help_support': {
                    'title': 'Help',
                    'icon': 'fas fa-life-ring',
                    'items': lambda: []
                }
            },
            'user_navigation': {},
            'current_user': None
        }


class ErrorLoggerService:
    """
    Self-contained error logging service
    Provides banking-grade error logging and monitoring
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.log_dir = os.path.join(os.getcwd(), 'logs', 'errors')
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Ensure error log directory exists"""
        try:
            os.makedirs(self.log_dir, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create error log directory: {e}")
    
    def log_error(self, error_type: str, message: str, details: Dict[str, Any] = None):
        """
        Log error with banking compliance standards
        """
        try:
            timestamp = datetime.now().isoformat()
            log_entry = {
                'timestamp': timestamp,
                'error_type': error_type,
                'message': message,
                'details': details or {},
                'user_id': getattr(current_user, 'id', 'anonymous') if current_user.is_authenticated else 'anonymous'
            }
            
            # Log to file
            log_file = os.path.join(self.log_dir, f'errors_{datetime.now().strftime("%Y%m%d")}.log')
            with open(log_file, 'a') as f:
                f.write(f"{timestamp} - {error_type}: {message}\n")
                if details:
                    f.write(f"Details: {details}\n")
                f.write("---\n")
            
            # Log to application logger
            self.logger.error(f"{error_type}: {message}", extra={'details': details})
            
        except Exception as e:
            # Fallback logging
            self.logger.error(f"Error logging failed: {e}")
    
    def log_security_event(self, event_type: str, message: str, user_id: str = None):
        """Log security-related events"""
        self.log_error(
            error_type=f"SECURITY_{event_type}",
            message=message,
            details={
                'user_id': user_id or getattr(current_user, 'id', 'anonymous'),
                'timestamp': datetime.now().isoformat(),
                'event_category': 'security'
            }
        )
    
    def log_template_error(self, template_name: str, error: Exception):
        """Log template rendering errors"""
        self.log_error(
            error_type="TEMPLATE_ERROR",
            message=f"Template rendering failed: {template_name}",
            details={
                'template': template_name,
                'exception': str(error),
                'exception_type': type(error).__name__
            }
        )
    
    def log_auth_error(self, auth_type: str, message: str, user_id: str = None):
        """Log authentication errors"""
        self.log_error(
            error_type=f"AUTH_{auth_type}",
            message=message,
            details={
                'user_id': user_id,
                'auth_category': auth_type.lower(),
                'timestamp': datetime.now().isoformat()
            }
        )

class BankingLogger:
    """
    Banking Logger Service for WebSocket handlers and real-time operations
    Provides structured logging for banking platform events
    """
    
    def __init__(self, module_name="banking_platform"):
        self.logger = logging.getLogger(module_name)
        self.module_name = module_name
    
    def log_info(self, message: str, extra_data: Dict = None):
        """Log informational messages"""
        try:
            if extra_data:
                self.logger.info(f"{message} | Data: {extra_data}")
            else:
                self.logger.info(message)
        except Exception as e:
            self.logger.error(f"Failed to log info message: {str(e)}")
    
    def log_error(self, error_type: str, message: str, extra_data: Dict = None):
        """Log error messages with context"""
        try:
            error_msg = f"[{error_type}] {message}"
            if extra_data:
                error_msg += f" | Context: {extra_data}"
            self.logger.error(error_msg)
        except Exception as e:
            self.logger.error(f"Failed to log error: {str(e)}")
    
    def log_warning(self, message: str, extra_data: Dict = None):
        """Log warning messages"""
        try:
            if extra_data:
                self.logger.warning(f"{message} | Data: {extra_data}")
            else:
                self.logger.warning(message)
        except Exception as e:
            self.logger.error(f"Failed to log warning: {str(e)}")
    
    def log_debug(self, message: str, extra_data: Dict = None):
        """Log debug messages"""
        try:
            if extra_data:
                self.logger.debug(f"{message} | Data: {extra_data}")
            else:
                self.logger.debug(message)
        except Exception as e:
            self.logger.error(f"Failed to log debug message: {str(e)}")
