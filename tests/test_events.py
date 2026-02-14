"""
Test cases for event functionality.
"""

import pytest
from datetime import datetime, timedelta
from flask import url_for
from models import Event, EventRegistration, db


class TestEventModel:
    """Test cases for Event model."""
    
    def test_event_repr(self, test_event):
        """Test event string representation."""
        assert repr(test_event) == f'<Event {test_event.title}>'
    
    def test_is_upcoming(self, test_event):
        """Test upcoming event detection."""
        assert test_event.is_upcoming
    
    def test_is_registration_open(self, test_event):
        """Test registration open status."""
        assert test_event.is_registration_open
    
    def test_available_spots(self, test_event):
        """Test available spots calculation."""
        assert test_event.available_spots == test_event.capacity
    
    def test_is_full(self, test_event):
        """Test full event detection."""
        assert not test_event.is_full


class TestEventRoutes:
    """Test cases for event routes."""
    
    def test_event_list_page(self, client):
        """Test event listing page loads."""
        response = client.get(url_for('events.index'))
        assert response.status_code == 200
        assert b'Upcoming Events' in response.data
    
    def test_event_detail_page(self, client, test_event):
        """Test event detail page loads."""
        response = client.get(url_for('events.event_detail', event_id=test_event.id))
        assert response.status_code == 200
        assert test_event.title.encode() in response.data
    
    def test_create_event_page_requires_login(self, client):
        """Test that create event page requires login."""
        response = client.get(url_for('events.create_event'), follow_redirects=True)
        assert response.status_code == 200
        assert b'Please log in' in response.data
    
    def test_create_event_page_loads(self, client, login_test_user):
        """Test that create event page loads for logged in user."""
        response = client.get(url_for('events.create_event'))
        assert response.status_code == 200
        assert b'Create New Event' in response.data
    
    def test_create_event(self, client, app):
        """Test successful event creation."""
        with app.app_context():
            # Create an organizer user
            from models import User
            organizer = User(
                username='eventorganizer',
                email='organizer@test.com',
                password='password123',
                first_name='Event',
                last_name='Organizer',
                role='organizer'
            )
            db.session.add(organizer)
            db.session.commit()
            
            # Login as organizer
            client.post(url_for('auth.login'), data={
                'email_or_username': organizer.username,
                'password': 'password123'
            }, follow_redirects=True)
            
            response = client.post(url_for('events.create_event'), data={
                'title': 'Test Event',
                'description': 'This is a test event description',
                'location': 'Test Location',
                'event_date': (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M'),
                'capacity': 100,
                'category': 'workshop',
                'status': 'published'
            }, follow_redirects=True)
            assert response.status_code == 200
            assert b'Event created successfully' in response.data


class TestEventRegistration:
    """Test cases for event registration."""
    
    def test_register_for_event(self, client, login_test_user, test_event, app):
        """Test successful event registration."""
        with app.app_context():
            response = client.post(
                url_for('events.register_for_event', event_id=test_event.id),
                follow_redirects=True
            )
            assert response.status_code == 200
            assert b'Successfully registered' in response.data
    
    def test_cannot_register_for_own_event(self, client, test_event, app):
        """Test that event creator cannot register for their own event."""
        with app.app_context():
            user = test_event.creator
            client.post(url_for('auth.login'), data={
                'email_or_username': user.username,
                'password': 'password123'
            }, follow_redirects=True)
            
            response = client.post(
                url_for('events.register_for_event', event_id=test_event.id),
                follow_redirects=True
            )
            assert response.status_code == 200
            assert b'cannot register for your own event' in response.data
    
    def test_unregister_from_event(self, client, login_test_user, test_event, app):
        """Test successful event unregistration."""
        with app.app_context():
            # First register
            client.post(
                url_for('events.register_for_event', event_id=test_event.id),
                follow_redirects=True
            )
            
            # Then unregister
            response = client.post(
                url_for('events.unregister_from_event', event_id=test_event.id),
                follow_redirects=True
            )
            assert response.status_code == 200
            assert b'Successfully unregistered' in response.data


class TestEventManagement:
    """Test cases for event management (edit/delete)."""
    
    def test_edit_event(self, client, test_event, app):
        """Test successful event edit."""
        with app.app_context():
            user = test_event.creator
            client.post(url_for('auth.login'), data={
                'email_or_username': user.username,
                'password': 'password123'
            }, follow_redirects=True)
            
            response = client.post(
                url_for('events.edit_event', event_id=test_event.id),
                data={
                    'title': 'Updated Event Title',
                    'description': test_event.description,
                    'location': test_event.location,
                    'event_date': test_event.event_date.strftime('%Y-%m-%dT%H:%M'),
                    'capacity': test_event.capacity,
                    'category': test_event.category,
                    'status': test_event.status
                },
                follow_redirects=True
            )
            assert response.status_code == 200
            assert b'Updated Event Title' in response.data
    
    def test_delete_event(self, client, test_event, app):
        """Test successful event deletion."""
        with app.app_context():
            user = test_event.creator
            client.post(url_for('auth.login'), data={
                'email_or_username': user.username,
                'password': 'password123'
            }, follow_redirects=True)
            
            response = client.post(
                url_for('events.delete_event', event_id=test_event.id),
                follow_redirects=True
            )
            assert response.status_code == 200
            assert b'deleted successfully' in response.data
