"""
CrowdConnect - Flask Extensions Initialization
=============================================

This module centralizes all Flask extension instances used throughout the application.
Flask extensions provide additional functionality without modifying the core framework:
- SQLAlchemy: Object-relational mapping (ORM) for database operations
- Flask-Login: User session management and authentication
- Flask-WTF CSRF: Cross-Site Request Forgery protection for forms
- Flask-Migrate: Database migration management

The init_extensions() function must be called during app factory setup to register
all extensions with the Flask application instance.

Author:  Sworoop
Date:    February 2026
Version: 1.0.0
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, AnonymousUserMixin
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

# Initialize SQLAlchemy database instance
db = SQLAlchemy()

# Initialize Flask-Login for user authentication
login_manager = LoginManager()


class AnonymousUser(AnonymousUserMixin):
    """Custom AnonymousUser class with additional methods for templates."""
    
    def is_organizer(self):
        """Return False for anonymous users."""
        return False
    
    def is_admin(self):
        """Return False for anonymous users."""
        return False
    
    @property
    def is_authenticated(self):
        """Return False for anonymous users."""
        return False
    
    @property
    def is_active(self):
        """Return False for anonymous users."""
        return False

# Initialize CSRF protection for forms
csrf = CSRFProtect()

# Initialize Flask-Migrate for database migrations
migrate = Migrate()


def init_extensions(app):
    """
    Initialize all Flask extensions with the application.
    
    Args:
        app: Flask application instance
    """
    # Initialize database
    db.init_app(app)
    
    # Initialize login manager
    login_manager.init_app(app)
    
    # Set custom anonymous user class
    login_manager.anonymous_user = AnonymousUser
    
    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Initialize migration
    migrate.init_app(app, db)
    
    # Configure login manager settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.refresh_view = 'auth.login'
    login_manager.needs_refresh_message = 'Please log in again to access this page.'
    login_manager.needs_refresh_message_category = 'info'
