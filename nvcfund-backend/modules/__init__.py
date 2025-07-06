"""
NVC Banking Platform - Enterprise Modular Architecture
Central module registry and management system
"""

from .core.registry import module_registry
from .core.navbar_builder import navbar_builder

__version__ = "1.0.0"
__all__ = ["module_registry", "navbar_builder"]