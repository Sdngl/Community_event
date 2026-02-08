"""
Flask extensions initialization.
Centralizes all Flask extension instances for the application.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

# Initialize SQLAlchemy database instance
db = SQLAlchemy()

# Initialize Flask-Login for user authentication
login_manager = LoginManager()

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
