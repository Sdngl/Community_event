"""
CrowdConnect - Event Management System
=====================================

Main application factory module for the Flask-based web application.
This file contains the core application setup, including:
- Flask app initialization and configuration
- Database extension initialization
- Blueprint registration for modular routing
- Custom template filters for datetime formatting
- CLI commands for database management

Author:  Sworoop
Date:    February 2026
Version: 1.0.0
"""

import os
from datetime import datetime
from flask import Flask, render_template
from config import config
from extensions import init_extensions
from routes import auth_bp, events_bp, admin_bp, main_bp


def create_app(config_name='default'):
    """
    Application factory for creating Flask app instances.
    
    Args:
        config_name: Configuration environment name
    
    Returns:
        Configured Flask application instance
    """
    # Create Flask application
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    init_extensions(app)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(admin_bp)
    
    # Configure shell context
    @app.shell_context_processor
    def make_shell_context():
        """
        Make database models available in Flask shell.
        
        Returns:
            Dictionary of objects for shell context
        """
        return {
            'db': db,
            'User': User,
            'Event': Event,
            'EventRegistration': EventRegistration,
            'Category': Category,
            'Tag': Tag,
            'Notification': Notification
        }
    
    # Register template filters
    @app.template_filter('datetime')
    def format_datetime(value, format='%B %d, %Y at %I:%M %p'):
        """Format datetime objects in templates."""
        if value is None:
            return ''
        return value.strftime(format)
    
    @app.template_filter('date')
    def format_date(value, format='%B %d, %Y'):
        """Format date objects in templates."""
        if value is None:
            return ''
        return value.strftime(format)
    
    @app.template_filter('time')
    def format_time(value, format='%I:%M %p'):
        """Format time objects in templates."""
        if value is None:
            return ''
        return value.strftime(format)
    
    # Add static file URL timestamp for cache busting
    @app.context_processor
    def inject_static():
        """
        Inject static URL with timestamp for cache busting.
        
        Returns:
            Dictionary with static_url function
        """
        def static_url(filename):
            """Generate static file URL with timestamp."""
            filepath = os.path.join(app.root_path, 'static', filename)
            if os.path.exists(filepath):
                timestamp = int(os.path.getmtime(filepath))
                return f'/static/{filename}?v={timestamp}'
            return f'/static/{filename}'
        return {'static_url': static_url, 'datetime': datetime}
    
    # Database creation command
    @app.cli.command('create-db')
    def create_db():
        """Create database tables."""
        db.create_all()
        print('Database tables created successfully.')
    
    # Seed database command
    @app.cli.command('seed-db')
    def seed_db():
        """Seed database with sample data."""
        from models import User, Event, EventRegistration
        from datetime import datetime, timedelta
        import random
        
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='System',
                last_name='Administrator',
                role='admin'
            )
            db.session.add(admin)
        
        # Create sample organizer if not exists
        if not User.query.filter_by(username='organizer').first():
            organizer = User(
                username='organizer',
                email='organizer@example.com',
                password='organizer123',
                first_name='Event',
                last_name='Organizer',
                role='organizer'
            )
            db.session.add(organizer)
        
        # Create sample user if not exists
        if not User.query.filter_by(username='user').first():
            user = User(
                username='user',
                email='user@example.com',
                password='user123',
                first_name='John',
                last_name='Doe',
                role='user'
            )
            db.session.add(user)
        
        db.session.commit()
        
        # Create sample events if none exist
        if Event.query.count() == 0:
            users = User.query.all()
            categories = ['conference', 'workshop', 'seminar', 'meetup', 'social', 'sports', 'cultural']
            locations = ['Main Hall', 'Conference Room A', 'Online', 'Community Center', 'Sports Complex']
            
            event_titles = [
                'Tech Innovation Conference 2024',
                'Web Development Workshop',
                'Community Networking Meetup',
                'Annual Sports Day',
                'Cultural Festival',
                'Python Programming Seminar',
                'Startup Pitch Competition',
                'Photography Workshop',
                'Health and Wellness Seminar',
                'Music and Art Festival'
            ]
            
            for i, title in enumerate(event_titles):
                event_date = datetime.utcnow() + timedelta(days=random.randint(1, 90))
                registration_deadline = event_date - timedelta(days=random.randint(1, 14))
                
                event = Event(
                    title=title,
                    description=f'This is a detailed description for {title}. Join us for an amazing experience filled with learning, networking, and fun activities.',
                    location=random.choice(locations),
                    event_date=event_date,
                    registration_deadline=registration_deadline,
                    capacity=random.randint(50, 200),
                    category=random.choice(categories),
                    status='published',
                    creator_id=random.choice(users).id
                )
                db.session.add(event)
            
            db.session.commit()
            print('Sample events created successfully.')
        
        print('Database seeding completed.')
    
    # Test route to verify app is working
    @app.route('/test')
    def test():
        """Test route for verifying app functionality."""
        return '<h1>Event Management System is running!</h1>'
    
    return app


# Import models for shell context
from extensions import db
from models import User, Event, EventRegistration


if __name__ == '__main__':
    # Create app instance
    app = create_app('development')
    
    # Get port from environment or use default
    port = int(os.environ.get('FLASK_RUN_PORT', 8000))
    host = os.environ.get('FLASK_RUN_HOST', '0.0.0.0')
    
    # Run the application
    app.run(debug=True, host=host, port=port)
