"""
Authentication routes for user registration, login, and logout.
Handles all authentication-related HTTP requests.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from forms import RegistrationForm, LoginForm, ChangePasswordForm
from models import User, db
from extensions import login_manager
from datetime import datetime


# Create authentication blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@login_manager.user_loader
def load_user(user_id):
    """
    Load user from database by ID for Flask-Login.
    
    Args:
        user_id: User's unique identifier
    
    Returns:
        User object or None
    """
    return User.query.get(int(user_id))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route.
    
    GET: Display registration form
    POST: Process registration form submission
    
    Returns:
        Rendered register template or redirect to login
    """
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # Create registration form
    form = RegistrationForm()
    
    # Process form submission
    if form.validate_on_submit():
        try:
            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                role='user'
            )
            
            # Add user to database
            db.session.add(user)
            db.session.commit()
            
            # Flash success message
            flash('Registration successful! Please log in to continue.', 'success')
            
            # Redirect to login page
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            # Rollback on error
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'danger')
    
    # Render registration template
    return render_template('auth/register.html', title='Register', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route.
    
    GET: Display login form
    POST: Process login form submission
    
    Returns:
        Rendered login template or redirect to intended page
    """
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # Create login form
    form = LoginForm()
    
    # Process form submission
    if form.validate_on_submit():
        try:
            # Try to find user by email or username
            user = User.query.filter(
                (User.email == form.email_or_username.data) | 
                (User.username == form.email_or_username.data)
            ).first()
            
            # Check if user exists and password is correct
            if user and user.verify_password(form.password.data):
                # Check if user account is active
                if not user.is_active:
                    flash('Your account has been deactivated. Please contact an administrator.', 'warning')
                    return redirect(url_for('auth.login'))
                
                # Log in user
                login_user(user, remember=form.remember.data)
                
                # Get next page from request
                next_page = request.args.get('next')
                
                # Flash welcome message
                flash(f'Welcome back, {user.username}!', 'success')
                
                # Redirect to next page or home
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
            else:
                flash('Invalid email/username or password. Please try again.', 'danger')
                
        except Exception as e:
            flash(f'Login failed: {str(e)}', 'danger')
    
    # Render login template
    return render_template('auth/login.html', title='Login', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """
    User logout route.
    
    Returns:
        Redirect to home page with logout message
    """
    # Get username for logout message
    username = current_user.username
    
    # Logout user
    logout_user()
    
    # Flash logout message
    flash(f'Goodbye, {username}! You have been logged out.', 'info')
    
    # Redirect to home page
    return redirect(url_for('main.home'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Change password route for logged-in users.
    
    GET: Display change password form
    POST: Process password change
    
    Returns:
        Rendered template or redirect on success
    """
    # Create change password form
    form = ChangePasswordForm()
    
    # Process form submission
    if form.validate_on_submit():
        try:
            # Verify old password
            if not current_user.verify_password(form.old_password.data):
                flash('Current password is incorrect.', 'danger')
                return render_template('user/change_password.html', title='Change Password', form=form)
            
            # Update password
            current_user.password = form.new_password.data
            db.session.commit()
            
            # Flash success message
            flash('Your password has been updated successfully.', 'success')
            
            # Redirect to profile page
            return redirect(url_for('user.profile', username=current_user.username))
            
        except Exception as e:
            # Rollback on error
            db.session.rollback()
            flash(f'Password change failed: {str(e)}', 'danger')
    
    # Render change password template
    return render_template('user/change_password.html', title='Change Password', form=form)


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    """
    Password reset request route.
    
    Note: This is a placeholder for future email functionality.
    """
    flash('Password reset functionality will be available soon.', 'info')
    return redirect(url_for('auth.login'))
