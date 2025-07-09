#!/usr/bin/env python3
"""
NVC Banking Platform - Main Entry Point
Production-ready banking and financial services platform
"""

from app_factory import create_app

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    print("Starting NVC Banking Platform...")
    print(f"Environment: {'Production' if not app.debug else 'Development'}")
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )