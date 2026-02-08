"""
Main routes for pages like home, about, and contact.
Handles general website navigation and user-facing pages.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from forms import UpdateProfileForm
from models import User, Event, EventRegistration
from datetime import datetime
from sqlalchemy import func


# Create main blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    """
    Home page route.
    
    Displays upcoming events and site introduction.
    
    Returns:
        Rendered home template
    """
    # Get upcoming published events
    upcoming_events = Event.query.filter(
        Event.status == 'published',
        Event.event_date > datetime.utcnow()
    ).order_by(Event.event_date.asc()).limit(6).all()
    
    # Get featured events (most registered)
    featured_events = Event.query.join(EventRegistration)\
        .filter(
            Event.status == 'published',
            Event.event_date > datetime.utcnow()
        )\
        .group_by(Event.id)\
        .order_by(func.count(EventRegistration.id).desc())\
        .limit(3)\
        .all()
    
    # Get statistics
    total_events = Event.query.filter_by(status='published').count()
    total_users = User.query.count()
    
    return render_template(
        'home.html',
        title='Home',
        upcoming_events=upcoming_events,
        featured_events=featured_events,
        total_events=total_events,
        total_users=total_users
    )


@main_bp.route('/about')
def about():
    """
    About page route.
    
    Returns:
        Rendered about template
    """
    return render_template('about.html', title='About Us')


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    Contact page route.
    
    GET: Display contact form
    POST: Process contact form (simulated)
    
    Returns:
        Rendered contact template
    """
    if request.method == 'POST':
        # Simulate contact form processing
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # In a real application, you would send an email here
        # For demonstration, we'll just flash a success message
        flash(f'Thank you, {name}! Your message has been sent. We will get back to you at {email}.', 'success')
        
        return redirect(url_for('main.home'))
    
    return render_template('contact.html', title='Contact Us')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    User dashboard route.
    
    Displays user's registered events, created events, and quick actions.
    
    Returns:
        Rendered dashboard template
    """
    # Get user's registrations
    registrations = EventRegistration.query.filter_by(
        user_id=current_user.id,
        status='registered'
    ).join(Event).all()
    
    # Get user's upcoming registrations
    upcoming_registrations = [
        r for r in registrations 
        if r.event.event_date > datetime.utcnow()
    ]
    
    # Get user's past registrations
    past_registrations = [
        r for r in registrations 
        if r.event.event_date <= datetime.utcnow()
    ]
    
    # Get user's created events
    my_events = Event.query.filter_by(
        creator_id=current_user.id
    ).order_by(Event.created_at.desc()).all()
    
    # Calculate statistics
    total_registrations = len(registrations)
    upcoming_count = len(upcoming_registrations)
    events_created = len(my_events)
    
    return render_template(
        'user/dashboard.html',
        title='Dashboard',
        upcoming_registrations=upcoming_registrations,
        past_registrations=past_registrations,
        my_events=my_events,
        total_registrations=total_registrations,
        upcoming_count=upcoming_count,
        events_created=events_created
    )


@main_bp.route('/profile/<username>')
@login_required
def profile(username):
    """
    User profile route.
    
    Args:
        username: Username of the profile to view
    
    Returns:
        Rendered profile template
    """
    # Get user by username
    user = User.query.filter_by(username=username).first_or_404()
    
    # Get user's events
    user_events = Event.query.filter_by(
        creator_id=user.id
    ).order_by(Event.created_at.desc()).limit(5).all()
    
    # Get registration count
    registration_count = EventRegistration.query.filter_by(
        user_id=user.id,
        status='registered'
    ).count()
    
    # Check if viewing own profile
    is_own_profile = (user.id == current_user.id)
    
    return render_template(
        'user/profile.html',
        title=f'{user.username}\'s Profile',
        user=user,
        user_events=user_events,
        registration_count=registration_count,
        is_own_profile=is_own_profile
    )


@main_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Edit profile route.
    
    GET: Display edit form
    POST: Process profile update
    
    Returns:
        Rendered edit form or redirect on success
    """
    # Create form with current user data
    form = UpdateProfileForm(
        original_username=current_user.username,
        original_email=current_user.email,
        username=current_user.username,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name
    )
    
    # Process form submission
    if form.validate_on_submit():
        try:
            # Update user data
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            
            # Save changes
            db.session.commit()
            
            # Flash success message
            flash('Your profile has been updated!', 'success')
            
            # Redirect to profile page
            return redirect(url_for('main.profile', username=current_user.username))
            
        except Exception as e:
            # Rollback on error
            db.session.rollback()
            flash(f'Failed to update profile: {str(e)}', 'danger')
    
    # Render edit template
    return render_template('user/edit_profile.html', title='Edit Profile', form=form)


@main_bp.route('/privacy')
def privacy():
    """
    Privacy policy page.
    
    Returns:
        Rendered privacy template
    """
    return render_template('privacy.html', title='Privacy Policy')


@main_bp.route('/terms')
def terms():
    """
    Terms of service page.
    
    Returns:
        Rendered terms template
    """
    return render_template('terms.html', title='Terms of Service')


@main_bp.route('/faq')
def faq():
    """
    Frequently asked questions page.
    
    Returns:
        Rendered FAQ template
    """
    return render_template('faq.html', title='FAQ')


# Error handlers
@main_bp.app_errorhandler(404)
def page_not_found(e):
    """
    Handle 404 errors.
    
    Args:
        e: Error exception
    
    Returns:
        Rendered 404 error template
    """
    return render_template('errors/404.html', title='Page Not Found'), 404


@main_bp.app_errorhandler(403)
def forbidden(e):
    """
    Handle 403 errors.
    
    Args:
        e: Error exception
    
    Returns:
        Rendered 403 error template
    """
    return render_template('errors/403.html', title='Access Forbidden'), 403


@main_bp.app_errorhandler(500)
def internal_server_error(e):
    """
    Handle 500 errors.
    
    Args:
        e: Error exception
    
    Returns:
        Rendered 500 error template
    """
    return render_template('errors/500.html', title='Server Error'), 500
