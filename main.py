
#!/usr/bin/env python3
"""
NVC Fund Banking Platform
Production-ready banking and financial services platform
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / 'nvcfund-backend'
sys.path.insert(0, str(backend_path))

print("Starting NVC Banking Platform with Pure Modular Architecture...")

try:
    from app_factory import create_app

    # Create the Flask application
    app = create_app()

    if __name__ == '__main__':
        print("Starting NVC Fund Banking Platform...")
        print(f"Environment: {'Production' if not app.debug else 'Development'}")

        # Additional startup logging
        try:
            from app.utils.logger import logger
            logger.log_api("Application startup initiated", startup=True)
        except Exception as e:
            print(f"Could not log startup: {e}")

        # Run the application
        app.run(
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000)),
            debug=bool(os.environ.get('DEBUG', False))
        )

except Exception as e:
    print(f"Failed to start application: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
