#!/usr/bin/env python
"""
CrowdConnect - Application Entry Point
====================================

This is the main entry point for running the CrowdConnect Flask application.
It creates an instance of the Flask app using the development configuration
and starts the development server.

Author:  Sworoop
Date:    February 2026
Version: 1.0.0
"""

from app import create_app

# Create application instance
app = create_app('development')

if __name__ == '__main__':
    # Run the Flask development server
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        use_reloader=True
    )
