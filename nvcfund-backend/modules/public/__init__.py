"""
Public Module for NVC Banking Platform
Handles all public-facing pages and contact functionality
"""

from flask import Blueprint
from .services import PublicService
from .chat.routes import chat_bp

__all__ = ['PublicService', 'chat_bp']

def create_public_blueprint():
    """Create and return the public blueprint"""
    from .routes import public_bp
    return public_bp