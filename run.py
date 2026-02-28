#!/usr/bin/env python
"""
CrowdConnect - Application Entry Point
====================================

This is the main entry point for running the CrowdConnect Flask application.
It supports both local development and Render deployment.

Author: Sworoop
Date: February 2026
Version: 1.1.0
"""

import os
from app import create_app

# Determine environment: 'development' locally, 'production' on Render
env = os.environ.get('FLASK_ENV', 'development')

# Create Flask app instance
app = create_app(env)

if __name__ == '__main__':
    # Local development only
    port = int(os.environ.get('PORT', 8000))  # Use Render PORT if set, else 8000
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        use_reloader=True
    )