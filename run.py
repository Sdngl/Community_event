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

# Determine environment
env = os.environ.get('FLASK_ENV', 'development')

# Create the Flask app
app = create_app(env)

# Only run server if this file is executed directly (local development)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        use_reloader=True
    )