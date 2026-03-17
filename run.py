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
from dotenv import load_dotenv

# Load environment variables from .env if it exists
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Determine environment: development locally, production on server
env = os.environ.get('FLASK_ENV', 'development')

# Create the Flask app
app = create_app(env)

# Only run the development server if executing locally
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=(env == 'development'),
        use_reloader=True
    )