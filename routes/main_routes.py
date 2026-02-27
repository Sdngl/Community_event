"""
CrowdConnect - Main Routes
==========================

This module handles all general website navigation and user-facing pages:
- Home page with upcoming and featured events
- About page with project information
- Contact page for user inquiries
- FAQ and privacy policy pages
- User dashboard and profile management

These routes are publicly accessible and form the main navigation structure
of the website. The dashboard requires authentication.

Author:  Sworoop
Date:    February 2026
Version: 1.0.0
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from forms import UpdateProfileForm
from models import User, Event, EventRegistration, Notification, db
from datetime import datetime, timedelta
from sqlalchemy import func, extract


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
    # Get upcoming published events (2 events per month)
    now = datetime.utcnow()
    all_upcoming = Event.query.filter(
        Event.status == 'published',
        Event.event_date > now
    ).order_by(Event.event_date.asc()).all()
    
    # Group events by month and limit to 2 per month
    events_by_month = {}
    for event in all_upcoming:
        month_key = (event.event_date.year, event.event_date.month)
        if month_key not in events_by_month:
            events_by_month[month_key] = []
        if len(events_by_month[month_key]) < 2:
            events_by_month[month_key].append(event)
    
    # Flatten back to list, sorted by date
    upcoming_events = []
    for month in sorted(events_by_month.keys()):
        upcoming_events.extend(events_by_month[month])
    
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

    # Analytics Data Preparation
    
    # 1. Registrations over time (last 30 days) for events created by user (if organizer)
    dates_data = []
    counts_data = []
    
    if current_user.is_organizer() and my_events:
        # Get all event IDs created by user
        event_ids = [e.id for e in my_events]
        
        if event_ids:
            # Query registrations for these events
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            daily_registrations = db.session.query(
                func.date(EventRegistration.registration_date).label('date'),
                func.count(EventRegistration.id).label('count')
            ).filter(
                EventRegistration.event_id.in_(event_ids),
                EventRegistration.registration_date >= thirty_days_ago
            ).group_by('date').all()
            
            # Format for Chart.js
            registrations_dict = {str(day.date): day.count for day in daily_registrations}
            
            # Fill in missing days
            for i in range(30):
                d = (datetime.utcnow() - timedelta(days=29-i)).strftime('%Y-%m-%d')
                dates_data.append(d)
                counts_data.append(registrations_dict.get(d, 0))

    # 2. Events by Category (for organizer)
    category_labels = []
    category_counts = []
    
    if current_user.is_organizer() and my_events:
        cat_stats = db.session.query(
            Event.category,
            func.count(Event.id)
        ).filter(
            Event.creator_id == current_user.id
        ).group_by(Event.category).all()
        
        for cat, count in cat_stats:
            category_labels.append(cat or 'Uncategorized')
            category_counts.append(count)
    
    return render_template(
        'user/dashboard.html',
        title='Dashboard',
        upcoming_registrations=upcoming_registrations,
        past_registrations=past_registrations,
        my_events=my_events,
        total_registrations=total_registrations,
        upcoming_count=upcoming_count,
        events_created=events_created,
        # Analytics Data
        dates_data=dates_data,
        counts_data=counts_data,
        category_labels=category_labels,
        category_counts=category_counts
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


@main_bp.route('/notifications')
@login_required
def notifications():
    """
    Display user notifications.
    
    Returns:
        Rendered notifications template
    """
    # Get all notifications for user
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).limit(50).all()
    
    # Get unread count
    unread_count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()
    
    return render_template(
        'notifications.html',
        title='Notifications',
        notifications=notifications,
        unread_count=unread_count
    )


@main_bp.route('/notifications/mark-read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    """
    Mark a notification as read.
    
    Args:
        notification_id: ID of the notification
    
    Returns:
        Redirect to notifications page
    """
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first_or_404()
    
    notification.mark_as_read()
    
    return redirect(url_for('main.notifications'))


@main_bp.route('/notifications/mark-all-read')
@login_required
def mark_all_notifications_read():
    """
    Mark all notifications as read.
    
    Returns:
        Redirect to notifications page
    """
    Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).update({'is_read': True})
    db.session.commit()
    
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('main.notifications'))


@main_bp.route('/api/notifications')
@login_required
def api_notifications():
    """
    API endpoint to get recent notifications.
    
    Returns:
        JSON response with notifications
    """
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).limit(10).all()
    
    unread_count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()
    
    return {
        'success': True,
        'notifications': [n.to_dict() for n in notifications],
        'unread_count': unread_count
    }
