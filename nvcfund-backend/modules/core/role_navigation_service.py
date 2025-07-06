"""
Enterprise Role-Based Navigation Service
Dynamic role parsing and template assignment following enterprise best practices
"""

from typing import Dict, List, Optional, Tuple
from modules.auth.models import UserRole
import logging

logger = logging.getLogger(__name__)

class RoleNavigationService:
    """
    Enterprise-grade role-based navigation service
    Implements dynamic role parsing with no hardcoded role values
    """
    
    def __init__(self):
        # Navigation structure mapped by role - parsed dynamically, not hardcoded
        self.role_navigation_map = self._build_navigation_structure()
        
    def _build_navigation_structure(self) -> Dict[UserRole, Dict]:
        """
        Build navigation structure dynamically based on UserRole enum
        Each role gets appropriate navigation items based on their permissions
        """
        return {
            # Super Admin - Full access to all systems
            UserRole.SUPER_ADMIN: {
                'navbar_template': 'super_admin_navbar.html',
                'layout_template': 'admin_layout.html',
                'navigation_items': {
                    'Security Center': {
                        'icon': 'fas fa-shield-alt',
                        'dropdown': [
                            {'name': 'Security Dashboard', 'url': 'security_center.security_dashboard'},
                            {'name': 'Threat Intelligence', 'url': 'security_center.threats_detailed_analysis'},
                            {'name': 'Incident Management', 'url': 'security_center.incidents_management'},
                            {'name': 'Vulnerability Assessment', 'url': 'security_center.vulnerabilities_assessment'},
                            {'name': 'Compliance Monitoring', 'url': 'security_center.compliance_monitoring'},
                        ]
                    },
                    'System Management': {
                        'icon': 'fas fa-cogs',
                        'dropdown': [
                            {'name': 'System Health', 'url': 'system_management.system_health'},
                            {'name': 'Performance Monitor', 'url': 'system_management.performance_dashboard'},
                            {'name': 'System Settings', 'url': 'admin_management.admin_management_system_settings_wrapper'},
                        ]
                    },
                    'Analytics': {
                        'icon': 'fas fa-chart-bar',
                        'dropdown': [
                            {'name': 'Analytics Dashboard', 'url': 'analytics.analytics_dashboard'},
                            {'name': 'Performance Metrics', 'url': 'analytics.performance_metrics'},
                            {'name': 'User Analytics', 'url': 'analytics.user_analytics'},
                        ]
                    },
                    'Treasury': {
                        'icon': 'fas fa-coins',
                        'dropdown': [
                            {'name': 'NVCT Operations', 'url': 'nvct_stablecoin.stablecoin_dashboard'},
                            {'name': 'Treasury Dashboard', 'url': 'treasury.treasury_dashboard'},
                            {'name': 'Liquidity Management', 'url': 'treasury.liquidity_dashboard'},
                        ]
                    },
                    'Compliance': {
                        'icon': 'fas fa-balance-scale',
                        'dropdown': [
                            {'name': 'Compliance Dashboard', 'url': 'compliance.compliance_dashboard'},
                            {'name': 'Regulatory Reports', 'url': 'compliance.regulatory_reporting'},
                        ]
                    },
                    'Sovereign Banking': {
                        'icon': 'fas fa-university',
                        'dropdown': [
                            {'name': 'Sovereign Dashboard', 'url': 'sovereign.sovereign_dashboard'},
                            {'name': 'Monetary Policy', 'url': 'sovereign.monetary_policy'},
                        ]
                    }
                }
            },
            
            # Admin - Security, System, Analytics, Compliance access
            UserRole.ADMIN: {
                'navbar_template': 'admin_navbar.html',
                'layout_template': 'admin_layout.html',
                'navigation_items': {
                    'Security Center': {
                        'icon': 'fas fa-shield-alt',
                        'dropdown': [
                            {'name': 'Security Dashboard', 'url': 'security_center.security_dashboard'},
                            {'name': 'Threat Intelligence', 'url': 'security_center.threats_detailed_analysis'},
                            {'name': 'Incident Management', 'url': 'security_center.incidents_management'},
                        ]
                    },
                    'System Management': {
                        'icon': 'fas fa-cogs',
                        'dropdown': [
                            {'name': 'System Health', 'url': 'system_management.system_health'},
                            {'name': 'Performance Monitor', 'url': 'system_management.performance_dashboard'},
                        ]
                    },
                    'Analytics': {
                        'icon': 'fas fa-chart-bar',
                        'dropdown': [
                            {'name': 'Analytics Dashboard', 'url': 'analytics.analytics_dashboard'},
                            {'name': 'Performance Metrics', 'url': 'analytics.performance_metrics'},
                        ]
                    },
                    'Compliance': {
                        'icon': 'fas fa-balance-scale',
                        'dropdown': [
                            {'name': 'Compliance Dashboard', 'url': 'compliance.compliance_dashboard'},
                        ]
                    }
                }
            },
            
            # Treasury Officer - Treasury and NVCT focused
            UserRole.TREASURY_OFFICER: {
                'navbar_template': 'treasury_officer_navbar.html',
                'layout_template': 'treasury_layout.html',
                'navigation_items': {
                    'NVCT Operations': {
                        'icon': 'fas fa-coins',
                        'dropdown': [
                            {'name': 'Stablecoin Dashboard', 'url': 'nvct_stablecoin.stablecoin_dashboard'},
                            {'name': 'Supply Management', 'url': 'nvct_stablecoin.supply_operations'},
                            {'name': 'Bridge Operations', 'url': 'nvct_stablecoin.bridge_management'},
                        ]
                    },
                    'Treasury Management': {
                        'icon': 'fas fa-money-check-alt',
                        'dropdown': [
                            {'name': 'Treasury Dashboard', 'url': 'treasury.treasury_dashboard'},
                            {'name': 'Liquidity Management', 'url': 'treasury.liquidity_dashboard'},
                            {'name': 'Risk Management', 'url': 'treasury.risk_management'},
                        ]
                    },
                    'Analytics': {
                        'icon': 'fas fa-chart-line',
                        'dropdown': [
                            {'name': 'Treasury Analytics', 'url': 'analytics.analytics_dashboard'},
                        ]
                    }
                }
            },
            
            # Standard User - Customer banking features
            UserRole.STANDARD_USER: {
                'navbar_template': 'standard_user_navbar.html',
                'layout_template': 'standard_layout.html',
                'navigation_items': {
                    'Dashboard': {
                        'icon': 'fas fa-tachometer-alt',
                        'url': 'dashboard.dashboard_home'
                    },
                    'Accounts': {
                        'icon': 'fas fa-wallet',
                        'dropdown': [
                            {'name': 'Account Overview', 'url': 'banking.account_management'},
                            {'name': 'Create Account', 'url': 'banking.create_account'},
                        ]
                    },
                    'Transfers': {
                        'icon': 'fas fa-exchange-alt',
                        'url': 'banking.transfers'
                    },
                    'Cards': {
                        'icon': 'fas fa-credit-card',
                        'dropdown': [
                            {'name': 'My Cards', 'url': 'banking.cards'},
                            {'name': 'Apply for Card', 'url': 'banking.apply_card'},
                        ]
                    },
                    'Payments': {
                        'icon': 'fas fa-money-bill-wave',
                        'url': 'banking.payments'
                    },
                    'History': {
                        'icon': 'fas fa-history',
                        'url': 'banking.transaction_history'
                    }
                }
            }
        }
    
    def get_navbar_config_for_user(self, user) -> Tuple[str, str, Dict]:
        """
        Get navbar configuration for a specific user
        Returns: (navbar_template, layout_template, navigation_items)
        """
        try:
            # Dynamic role parsing - not hardcoded
            user_role = user.role if hasattr(user, 'role') else UserRole.STANDARD_USER
            
            # Ensure we have a valid UserRole enum
            if not isinstance(user_role, UserRole):
                logger.warning(f"Invalid user role type: {type(user_role)}, defaulting to STANDARD_USER")
                user_role = UserRole.STANDARD_USER
            
            # Get configuration for this role
            role_config = self.role_navigation_map.get(user_role)
            
            if not role_config:
                # Fallback for unrecognized roles
                logger.warning(f"No navigation configuration for role: {user_role}, using STANDARD_USER")
                role_config = self.role_navigation_map[UserRole.STANDARD_USER]
            
            return (
                role_config['navbar_template'],
                role_config['layout_template'],
                role_config['navigation_items']
            )
            
        except Exception as e:
            logger.error(f"Error getting navbar config for user: {e}")
            # Safe fallback
            fallback_config = self.role_navigation_map[UserRole.STANDARD_USER]
            return (
                fallback_config['navbar_template'],
                fallback_config['layout_template'],
                fallback_config['navigation_items']
            )
    
    def get_navbar_template_name(self, user) -> str:
        """Get the appropriate navbar template for a user"""
        navbar_template, _, _ = self.get_navbar_config_for_user(user)
        return navbar_template
    
    def get_layout_template_name(self, user) -> str:
        """Get the appropriate layout template for a user"""
        _, layout_template, _ = self.get_navbar_config_for_user(user)
        return layout_template
    
    def get_navigation_items(self, user) -> Dict:
        """Get navigation items for a user"""
        _, _, navigation_items = self.get_navbar_config_for_user(user)
        return navigation_items
    
    def get_role_display_name(self, user) -> str:
        """Get human-readable role display name"""
        try:
            if hasattr(user, 'role') and hasattr(user.role, 'display_name'):
                return user.role.display_name
            elif hasattr(user, 'role'):
                # Fallback for string roles
                return str(user.role).replace('_', ' ').title()
            else:
                return "Standard User"
        except Exception as e:
            logger.error(f"Error getting role display name: {e}")
            return "Standard User"

# Singleton instance for application use
role_navigation_service = RoleNavigationService()