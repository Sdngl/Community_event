"""
Routes package for the Event Management System.
Contains all route blueprints for modular application structure.
"""

from routes.auth_routes import auth_bp
from routes.event_routes import events_bp
from routes.admin_routes import admin_bp
from routes.main_routes import main_bp

__all__ = ['auth_bp', 'events_bp', 'admin_bp', 'main_bp']
