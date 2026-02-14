"""
Test cases for authentication functionality.
"""

import pytest
from flask import url_for
from models import User, db


class TestAuthentication:
    """Test cases for user authentication."""
    
    def test_register_page_loads(self, client):
        """Test that registration page loads successfully."""
        response = client.get(url_for('auth.register'))
        assert response.status_code == 200
        assert b'Register' in response.data
    
    def test_login_page_loads(self, client):
        """Test that login page loads successfully."""
        response = client.get(url_for('auth.login'))
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_successful_registration(self, client, app):
        """Test successful user registration."""
        with app.app_context():
            response = client.post(url_for('auth.register'), data={
                'username': 'newuser',
                'email': 'newuser@test.com',
                'password': 'password123',
                'confirm_password': 'password123',
                'first_name': 'New',
                'last_name': 'User'
            }, follow_redirects=True)
            assert response.status_code == 200
            assert b'Registration successful' in response.data
    
    def test_registration_with_existing_username(self, client, app, test_user):
        """Test registration with existing username fails."""
        with app.app_context():
            response = client.post(url_for('auth.register'), data={
                'username': test_user.username,
                'email': 'different@test.com',
                'password': 'password123',
                'confirm_password': 'password123',
                'first_name': 'Different',
                'last_name': 'User'
            }, follow_redirects=True)
            assert response.status_code == 200
            assert b'already taken' in response.data
    
    def test_successful_login(self, client, test_user):
        """Test successful user login."""
        response = client.post(url_for('auth.login'), data={
            'email_or_username': test_user.username,
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Welcome back' in response.data
    
    def test_failed_login_wrong_password(self, client, test_user):
        """Test login with wrong password fails."""
        response = client.post(url_for('auth.login'), data={
            'email_or_username': test_user.username,
            'password': 'wrongpassword'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid' in response.data
    
    def test_logout(self, client, login_test_user):
        """Test user logout."""
        response = client.get(url_for('auth.logout'), follow_redirects=True)
        assert response.status_code == 200
        assert b'logged out' in response.data
    
    def test_access_protected_route_without_login(self, client):
        """Test that protected routes redirect to login."""
        response = client.get(url_for('main.dashboard'), follow_redirects=True)
        assert response.status_code == 200
        assert b'Please log in' in response.data


class TestUserModel:
    """Test cases for User model."""
    
    def test_password_hashing(self, app, test_user):
        """Test that password is properly hashed."""
        with app.app_context():
            assert test_user.verify_password('password123')
            assert not test_user.verify_password('wrongpassword')
    
    def test_user_repr(self, test_user):
        """Test user string representation."""
        assert repr(test_user) == f'<User {test_user.username}>'
    
    def test_is_admin(self, test_user, admin_user):
        """Test admin role detection."""
        assert not test_user.is_admin()
        assert admin_user.is_admin()
    
    def test_full_name(self, test_user):
        """Test full name property."""
        test_user.first_name = 'John'
        test_user.last_name = 'Doe'
        assert test_user.full_name == 'John Doe'
