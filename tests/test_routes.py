"""
Test cases for general routes and pages.
"""

import pytest
from flask import url_for


class TestMainRoutes:
    """Test cases for main routes."""
    
    def test_home_page(self, client):
        """Test home page loads successfully."""
        response = client.get(url_for('main.home'))
        assert response.status_code == 200
        assert b'EventHub' in response.data
        assert b'Upcoming Events' in response.data
    
    def test_about_page(self, client):
        """Test about page loads successfully."""
        response = client.get(url_for('main.about'))
        assert response.status_code == 200
        assert b'About EventHub' in response.data
    
    def test_contact_page(self, client):
        """Test contact page loads successfully."""
        response = client.get(url_for('main.contact'))
        assert response.status_code == 200
        assert b'Contact Us' in response.data


class TestDashboard:
    """Test cases for dashboard functionality."""
    
    def test_dashboard_requires_login(self, client):
        """Test that dashboard requires login."""
        response = client.get(url_for('main.dashboard'), follow_redirects=True)
        assert response.status_code == 200
        assert b'Please log in' in response.data
    
    def test_dashboard_loads(self, client, login_test_user):
        """Test that dashboard loads for logged in user."""
        response = client.get(url_for('main.dashboard'))
        assert response.status_code == 200
        assert b'Dashboard' in response.data
    
    def test_profile_page(self, client, login_test_user):
        """Test profile page loads."""
        response = client.get(url_for('main.profile', username=login_test_user.username))
        assert response.status_code == 200
        assert login_test_user.username.encode() in response.data


class TestAdminRoutes:
    """Test cases for admin routes."""
    
    def test_admin_requires_admin(self, client, login_test_user):
        """Test that admin routes require admin role."""
        response = client.get(url_for('admin.dashboard'), follow_redirects=True)
        assert response.status_code == 200
        assert b'Access Forbidden' in response.data
    
    def test_admin_dashboard_loads(self, client, login_admin):
        """Test that admin dashboard loads for admin user."""
        response = client.get(url_for('admin.dashboard'))
        assert response.status_code == 200
        assert b'Admin Dashboard' in response.data
    
    def test_manage_users_requires_admin(self, client, login_test_user):
        """Test that manage users requires admin role."""
        response = client.get(url_for('admin.manage_users'), follow_redirects=True)
        assert response.status_code == 200
        assert b'Access Forbidden' in response.data
    
    def test_manage_events_requires_admin(self, client, login_test_user):
        """Test that manage events requires admin role."""
        response = client.get(url_for('admin.manage_events'), follow_redirects=True)
        assert response.status_code == 200
        assert b'Access Forbidden' in response.data


class TestErrorHandlers:
    """Test cases for error handlers."""
    
    def test_404_error(self, client):
        """Test 404 error page."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        assert b'404' in response.data
        assert b'Page Not Found' in response.data
    
    def test_403_error(self, client, login_test_user):
        """Test 403 error page."""
        response = client.get(url_for('admin.dashboard'), follow_redirects=False)
        assert response.status_code == 403


class TestSearchAndFilters:
    """Test cases for search and filter functionality."""
    
    def test_event_list_with_search(self, client, test_event):
        """Test event list with search query."""
        response = client.get(url_for('events.index', search=test_event.title))
        assert response.status_code == 200
        assert test_event.title.encode() in response.data
    
    def test_event_list_with_category(self, client, test_event):
        """Test event list with category filter."""
        response = client.get(url_for('events.index', category=test_event.category))
        assert response.status_code == 200
    
    def test_pagination(self, client, app):
        """Test pagination on event list."""
        with app.app_context():
            # Create multiple events
            from models import Event
            for i in range(15):
                event = Event(
                    title=f'Event {i}',
                    description=f'Description for event {i}',
                    location=f'Location {i}',
                    event_date=datetime.utcnow() + timedelta(days=i),
                    capacity=100,
                    category='workshop',
                    status='published',
                    creator_id=1
                )
                db.session.add(event)
            db.session.commit()
            
            response = client.get(url_for('events.index', page=1))
            assert response.status_code == 200
