"""
Template Context Processors
Enterprise-grade template context management for role-based navigation
"""

from flask import current_app
from flask_login import current_user
from modules.core.role_navigation_service import role_navigation_service
from modules.auth.models import UserRole
import logging

logger = logging.getLogger(__name__)

def register_template_context(app):
    """Register template context processors with the Flask app"""
    
    @app.context_processor
    def inject_role_navigation():
        """
        Inject role-based navigation variables into all templates
        Dynamic role parsing - no hardcoded values
        """
        context = {}
        
        try:
            if current_user.is_authenticated:
                # Get dynamic navigation configuration for current user
                navbar_template, layout_template, navigation_items = role_navigation_service.get_navbar_config_for_user(current_user)
                role_display = role_navigation_service.get_role_display_name(current_user)
                
                context.update({
                    'user_navbar_template': navbar_template,
                    'user_layout_template': layout_template,
                    'user_navigation_items': navigation_items,
                    'user_role_display': role_display,
                    'user_role_enum': current_user.role if hasattr(current_user, 'role') else UserRole.STANDARD_USER
                })
            else:
                # Default context for non-authenticated users
                context.update({
                    'user_navbar_template': 'public_navbar.html',
                    'user_layout_template': 'public_layout.html',
                    'user_navigation_items': {},
                    'user_role_display': 'Guest',
                    'user_role_enum': None
                })
                
        except Exception as e:
            logger.error(f"Error injecting role navigation context: {e}")
            # Safe fallback
            context.update({
                'user_navbar_template': 'standard_user_navbar.html',
                'user_layout_template': 'standard_layout.html',
                'user_navigation_items': {},
                'user_role_display': 'Standard User',
                'user_role_enum': UserRole.STANDARD_USER
            })
        
        return context
    
    @app.context_processor
    def inject_rbac_functions():
        """
        Inject RBAC permission checking functions into templates
        Following enterprise best practices for secure template rendering
        """
        def check_permission(permission_string):
            """
            Check if current user has specific permission
            Enterprise-grade permission checking for template conditionals
            """
            if not current_user.is_authenticated:
                return False
            
            # Define role-permission mappings following banking security standards
            ROLES_FOR_PERMISSION = {
                # Banking Operations
                'can_view_accounts': [UserRole.STANDARD_USER, UserRole.BUSINESS_USER, UserRole.CUSTOMER_SERVICE, 
                                     UserRole.BRANCH_MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_initiate_transfer': [UserRole.STANDARD_USER, UserRole.BUSINESS_USER, UserRole.CUSTOMER_SERVICE,
                                        UserRole.BRANCH_MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_view_all_transactions': [UserRole.BRANCH_MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
                
                # Administrative Functions
                'can_access_admin_dashboard': [UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_manage_users': [UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_view_system_logs': [UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_modify_system_settings': [UserRole.SUPER_ADMIN],
                
                # Treasury Operations
                'can_access_treasury': [UserRole.TREASURY_OFFICER, UserRole.ASSET_LIABILITY_MANAGER, 
                                       UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_manage_liquidity': [UserRole.TREASURY_OFFICER, UserRole.ASSET_LIABILITY_MANAGER],
                'can_access_nvct_operations': [UserRole.TREASURY_OFFICER, UserRole.SOVEREIGN_BANKER,
                                              UserRole.CENTRAL_BANK_GOVERNOR, UserRole.SUPER_ADMIN],
                
                # Sovereign Banking
                'can_access_sovereign_banking': [UserRole.SOVEREIGN_BANKER, UserRole.CENTRAL_BANK_GOVERNOR, 
                                               UserRole.SUPER_ADMIN],
                'can_manage_monetary_policy': [UserRole.CENTRAL_BANK_GOVERNOR, UserRole.SUPER_ADMIN],
                
                # Compliance & Risk
                'can_access_compliance': [UserRole.COMPLIANCE_OFFICER, UserRole.RISK_MANAGER, 
                                        UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_manage_kyc': [UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_access_risk_management': [UserRole.RISK_MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
                
                # Branch Operations & Customer Service
                'can_access_branch_management': [UserRole.BRANCH_MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_manage_customer_service': [UserRole.CUSTOMER_SERVICE, UserRole.BRANCH_MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_handle_customer_issues': [UserRole.CUSTOMER_SERVICE, UserRole.BRANCH_MANAGER],
                'can_approve_branch_transactions': [UserRole.BRANCH_MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
                
                # Institutional Banking
                'can_access_institutional': [UserRole.INSTITUTIONAL_BANKER, UserRole.CORRESPONDENT_BANKER,
                                           UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_manage_correspondent_banks': [UserRole.CORRESPONDENT_BANKER, UserRole.SUPER_ADMIN],
                'can_access_wholesale_banking': [UserRole.INSTITUTIONAL_BANKER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
                
                # Asset Liability Management
                'can_access_alm': [UserRole.ASSET_LIABILITY_MANAGER, UserRole.TREASURY_OFFICER, UserRole.SUPER_ADMIN],
                'can_manage_interest_rates': [UserRole.ASSET_LIABILITY_MANAGER, UserRole.TREASURY_OFFICER],
                'can_access_balance_sheet': [UserRole.ASSET_LIABILITY_MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
                
                # Security Center
                'can_access_security_center': [UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_view_security_logs': [UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_manage_security_settings': [UserRole.SUPER_ADMIN]
            }
            
            # Check if the user's current role is allowed for this permission
            allowed_roles = ROLES_FOR_PERMISSION.get(permission_string, [])
            return current_user.role in allowed_roles
        
        def has_role(role):
            """Check if current user has specific role"""
            if not current_user.is_authenticated:
                return False
            return current_user.role == role
        
        def is_privileged_user():
            """Check if user has privileged access"""
            if not current_user.is_authenticated:
                return False
            return current_user.is_privileged_user()
        
        def can_access_module(module_name):
            """Check if user can access specific banking module"""
            if not current_user.is_authenticated:
                return False
            
            module_permissions = {
                'admin_management': 'can_access_admin_dashboard',
                'security_center': 'can_access_security_center', 
                'treasury': 'can_access_treasury',
                'sovereign': 'can_access_sovereign_banking',
                'compliance': 'can_access_compliance',
                'institutional': 'can_access_institutional',
                'nvct_stablecoin': 'can_access_nvct_operations'
            }
            
            required_permission = module_permissions.get(module_name)
            if required_permission:
                return check_permission(required_permission)
            return False
        
        return {
            'check_permission': check_permission,
            'has_role': has_role,
            'is_privileged_user': is_privileged_user,
            'can_access_module': can_access_module,
            'get_role_navigation': role_navigation_service.get_navbar_config_for_user,
            'get_role_display': role_navigation_service.get_role_display_name,
            'UserRole': UserRole  # Make UserRole enum available in templates
        }