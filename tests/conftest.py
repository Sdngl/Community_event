"""
Pytest configuration and fixtures.
"""

import pytest
from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models import User, Event


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            username='testuser',
            email='testuser@test.com',
            password='password123',
            first_name='Test',
            last_name='User',
            role='user'
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def admin_user(app):
    """Create a test admin user."""
    with app.app_context():
        user = User(
            username='testadmin',
            email='testadmin@test.com',
            password='admin123',
            first_name='Test',
            last_name='Admin',
            role='admin'
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def test_event(app, test_user):
    """Create a test event."""
    with app.app_context():
        event = Event(
            title='Test Event',
            description='This is a test event description',
            location='Test Location',
            event_date=datetime.utcnow() + timedelta(days=7),
            registration_deadline=datetime.utcnow() + timedelta(days=1),
            capacity=100,
            category='workshop',
            status='published',
            creator_id=test_user.id
        )
        db.session.add(event)
        db.session.commit()
        return event


@pytest.fixture
def login_test_user(client, test_user):
    """Log in test user."""
    client.post('/auth/login', data={
        'email_or_username': test_user.username,
        'password': 'password123'
    }, follow_redirects=True)
    return test_user


@pytest.fixture
def login_admin(client, admin_user):
    """Log in admin user."""
    client.post('/auth/login', data={
        'email_or_username': admin_user.username,
        'password': 'admin123'
    }, follow_redirects=True)
    return admin_user
