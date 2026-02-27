"""
CrowdConnect - Routes Package
============================

This package contains all route blueprints for modular application structure.
Blueprints allow for organized code separation and reusable route components.

Exported Blueprints:
- auth_bp: Authentication routes (login, register, logout)
- events_bp: Event management routes (CRUD operations)
- admin_bp: Administrative routes (system management)
- main_bp: General pages (home, about, contact)

Author:  Sworoop
Date:    February 2026
Version: 1.0.0
"""

from routes.auth_routes import auth_bp
from routes.event_routes import events_bp
from routes.admin_routes import admin_bp
from routes.main_routes import main_bp

__all__ = ['auth_bp', 'events_bp', 'admin_bp', 'main_bp']
