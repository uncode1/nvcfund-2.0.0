"""
Main Entry Point - Pure Modular Architecture
NVC Banking Platform using enterprise-grade modular structure
"""

from app_factory import create_app
import os

# Create application using the modular app factory pattern
app = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)