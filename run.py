#!/usr/bin/env python
"""
EventHub - Community Event Management System
Entry point for running the Flask application.
"""

from app import create_app

# Create application instance
app = create_app('development')

if __name__ == '__main__':
    # Run the Flask development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )
