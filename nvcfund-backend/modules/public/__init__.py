"""
Public Module for NVC Banking Platform
Handles all public-facing pages and contact functionality
"""

from flask import Blueprint
from .services import PublicService

__all__ = ['PublicService']

def create_public_blueprint():
    """Create and return the public blueprint"""
    from .routes import public_bp
    return public_bp