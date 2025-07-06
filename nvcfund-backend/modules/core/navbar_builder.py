"""
Navbar Builder for Modular Architecture
Dynamically builds navigation based on active modules and user permissions
"""

from typing import Dict, List, Any
from .registry import module_registry

class NavbarBuilder:
    """Builds navigation menus based on active modules and user roles"""

    def __init__(self):
        self.navigation_items = {}
        self._initialize_default_items()

    def _initialize_default_items(self):
        """Initialize default navigation items"""
        self.navigation_items = {
            'standard': {
                'Dashboard': {'route': 'dashboard.main_dashboard', 'icon': 'fas fa-tachometer-alt'},
                'Accounts': {'route': 'accounts.overview', 'icon': 'fas fa-university'},
                'Transfers': {'route': 'transfers.create', 'icon': 'fas fa-exchange-alt'},
                'Cards': {'route': 'cards.overview', 'icon': 'fas fa-credit-card'},
                'History': {'route': 'transactions.history', 'icon': 'fas fa-history'}
            },
            'treasury_officer': {
                'Dashboard': {'route': 'dashboard.main_dashboard', 'icon': 'fas fa-tachometer-alt'},
                'NVCT Operations': {'route': 'treasury.nvct_management', 'icon': 'fas fa-coins'},
                'Liquidity': {'route': 'treasury.liquidity', 'icon': 'fas fa-water'},
                'Risk Management': {'route': 'treasury.risk', 'icon': 'fas fa-shield-alt'},
                'Treasury Reports': {'route': 'treasury.reports', 'icon': 'fas fa-chart-line'}
            },
            'admin': {
                'Admin Dashboard': {'route': 'admin.dashboard', 'icon': 'fas fa-cogs'},
                'Users': {'route': 'admin.users', 'icon': 'fas fa-users'},
                'System': {'route': 'admin.system', 'icon': 'fas fa-server'},
                'Security': {'route': 'admin.security', 'icon': 'fas fa-lock'},
                'Compliance': {'route': 'admin.compliance', 'icon': 'fas fa-balance-scale'},
                'Reports': {'route': 'admin.reports', 'icon': 'fas fa-chart-bar'}
            }
        }

    def build_navbar(self, user_role: str = 'standard') -> Dict[str, Any]:
        """Build navbar for specific user role"""
        try:
            # Get base navigation items for user role
            base_items = self.navigation_items.get(user_role, self.navigation_items['standard'])

            # Get modules accessible to user
            accessible_modules = module_registry.get_user_modules(user_role)

            # Filter items based on module availability
            filtered_items = {}
            for name, item in base_items.items():
                # Extract module name from route
                module_name = item['route'].split('.')[0]
                if module_name in accessible_modules or module_name in ['dashboard', 'main']:
                    filtered_items[name] = item

            return {
                'items': filtered_items,
                'user_role': user_role,
                'module_count': len(accessible_modules)
            }

        except Exception as e:
            # Fallback to basic navigation
            return {
                'items': {'Dashboard': {'route': 'public.index', 'icon': 'fas fa-home'}},
                'user_role': user_role,
                'module_count': 0,
                'error': str(e)
            }

    def get_dropdowns(self, user_role: str = 'standard') -> Dict[str, List[Dict]]:
        """Get dropdown menu items for user role"""
        dropdowns = {
            'standard': {
                'Banking': [
                    {'name': 'Account Services', 'route': 'accounts.overview', 'icon': 'fas fa-university'},
                    {'name': 'Transfers', 'route': 'transfers.create', 'icon': 'fas fa-exchange-alt'},
                    {'name': 'Bill Pay', 'route': 'transfers.bill_pay', 'icon': 'fas fa-file-invoice-dollar'}
                ],
                'Cards': [
                    {'name': 'View Cards', 'route': 'cards.overview', 'icon': 'fas fa-credit-card'},
                    {'name': 'Apply for Card', 'route': 'cards.apply', 'icon': 'fas fa-plus-circle'},
                    {'name': 'Digital Wallets', 'route': 'cards.digital', 'icon': 'fas fa-mobile-alt'}
                ]
            },
            'treasury_officer': {
                'Treasury': [
                    {'name': 'NVCT Management', 'route': 'treasury.nvct_management', 'icon': 'fas fa-coins'},
                    {'name': 'Asset Backing', 'route': 'treasury.asset_backing', 'icon': 'fas fa-chart-pie'},
                    {'name': 'Liquidity Pool', 'route': 'treasury.liquidity', 'icon': 'fas fa-water'}
                ],
                'Risk': [
                    {'name': 'Risk Dashboard', 'route': 'treasury.risk', 'icon': 'fas fa-shield-alt'},
                    {'name': 'Compliance', 'route': 'treasury.compliance', 'icon': 'fas fa-balance-scale'}
                ]
            },
            'admin': {
                'System': [
                    {'name': 'System Health', 'route': 'admin.system.health', 'icon': 'fas fa-heartbeat'},
                    {'name': 'Modules', 'route': 'admin.system.modules', 'icon': 'fas fa-puzzle-piece'},
                    {'name': 'Performance', 'route': 'admin.system.performance', 'icon': 'fas fa-tachometer-alt'}
                ],
                'Security': [
                    {'name': 'Security Dashboard', 'route': 'admin.security.dashboard', 'icon': 'fas fa-shield-alt'},
                    {'name': 'Audit Logs', 'route': 'admin.security.audit', 'icon': 'fas fa-list-alt'},
                    {'name': 'User Sessions', 'route': 'admin.security.sessions', 'icon': 'fas fa-users-cog'}
                ]
            }
        }

        return dropdowns.get(user_role, dropdowns['standard'])

    def add_custom_item(self, user_role: str, name: str, route: str, icon: str = 'fas fa-link'):
        """Add custom navigation item for specific user role"""
        if user_role not in self.navigation_items:
            self.navigation_items[user_role] = {}

        self.navigation_items[user_role][name] = {
            'route': route,
            'icon': icon
        }

# Global navbar builder instance
navbar_builder = NavbarBuilder()