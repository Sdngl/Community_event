"""
Admin routes for system management.
Handles user management, event management, and administrative functions.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from forms import AdminUserEditForm, AdminEventEditForm
from models import User, Event, EventRegistration, db
from datetime import datetime


# Create admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.before_request
@login_required
def admin_required():
    """
    Before request hook to check admin access.
    
    Ensures only admin users can access admin routes.
    """
    if not current_user.is_admin():
        abort(403)


@admin_bp.route('/')
def dashboard():
    """
    Admin dashboard with overview statistics.
    
    Returns:
        Rendered admin dashboard template
    """
    # Get statistics
    total_users = User.query.count()
    total_events = Event.query.count()
    total_registrations = EventRegistration.query.count()
    
    # Get recent registrations
    recent_registrations = EventRegistration.query\
        .join(Event)\
        .order_by(EventRegistration.registration_date.desc())\
        .limit(10)\
        .all()
    
    # Get recent events
    recent_events = Event.query\
        .order_by(Event.created_at.desc())\
        .limit(5)\
        .all()
    
    # Get users by role
    admin_count = User.query.filter_by(role='admin').count()
    organizer_count = User.query.filter_by(role='organizer').count()
    user_count = User.query.filter_by(role='user').count()
    
    # Get events by status
    published_count = Event.query.filter_by(status='published').count()
    draft_count = Event.query.filter_by(status='draft').count()
    cancelled_count = Event.query.filter_by(status='cancelled').count()
    
    # Get upcoming events
    upcoming_events = Event.query.filter(
        Event.event_date > datetime.utcnow(),
        Event.status == 'published'
    ).order_by(Event.event_date.asc()).limit(5).all()
    
    return render_template(
        'admin/admin_dashboard.html',
        title='Admin Dashboard',
        total_users=total_users,
        total_events=total_events,
        total_registrations=total_registrations,
        recent_registrations=recent_registrations,
        recent_events=recent_events,
        admin_count=admin_count,
        organizer_count=organizer_count,
        user_count=user_count,
        published_count=published_count,
        draft_count=draft_count,
        cancelled_count=cancelled_count,
        upcoming_events=upcoming_events
    )


@admin_bp.route('/users')
def manage_users():
    """
    Display all users with management options.
    
    Query parameters:
        page: Page number
        role: Filter by role
        search: Search by username or email
    
    Returns:
        Rendered user management template
    """
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    role = request.args.get('role', '')
    search = request.args.get('search', '')
    
    # Build query
    query = User.query
    
    # Apply filters
    if role:
        query = query.filter_by(role=role)
    
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    # Order by creation date
    query = query.order_by(User.created_at.desc())
    
    # Paginate
    pagination = query.paginate(
        page=page,
        per_page=20,
        error_out=False
    )
    
    return render_template(
        'admin/manage_users.html',
        title='Manage Users',
        users=pagination.items,
        pagination=pagination,
        role=role,
        search=search
    )


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    """
    Edit user details.
    
    Args:
        user_id: ID of the user to edit
    
    Returns:
        Rendered edit form or redirect on success
    """
    # Get user by ID
    user = User.query.get_or_404(user_id)
    
    # Prevent editing other admins
    if user.is_admin() and user.id != current_user.id:
        flash('You cannot edit other admin accounts.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    # Create form with current user data
    form = AdminUserEditForm(
        original_username=user.username,
        original_email=user.email,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active
    )
    
    # Process form submission
    if form.validate_on_submit():
        try:
            # Update user data
            user.username = form.username.data
            user.email = form.email.data
            user.role = form.role.data
            user.is_active = form.is_active.data
            
            # Save changes
            db.session.commit()
            
            # Flash success message
            flash(f'User {user.username} updated successfully!', 'success')
            
            # Redirect to user management
            return redirect(url_for('admin.manage_users'))
            
        except Exception as e:
            # Rollback on error
            db.session.rollback()
            flash(f'Failed to update user: {str(e)}', 'danger')
    
    # Render edit template
    return render_template('admin/edit_user.html', title='Edit User', form=form, user=user)


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """
    Delete a user account.
    
    Args:
        user_id: ID of the user to delete
    
    Returns:
        Redirect to user management
    """
    # Get user by ID
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself or other admins
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    if user.is_admin():
        flash('Admin accounts cannot be deleted.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    try:
        # Delete user (cascades to events and registrations)
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        # Flash success message
        flash(f'User {username} deleted successfully!', 'success')
        
    except Exception as e:
        # Rollback on error
        db.session.rollback()
        flash(f'Failed to delete user: {str(e)}', 'danger')
    
    # Redirect to user management
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/events')
def manage_events():
    """
    Display all events with management options.
    
    Query parameters:
        page: Page number
        status: Filter by status
        category: Filter by category
    
    Returns:
        Rendered event management template
    """
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    category = request.args.get('category', '')
    
    # Build query
    query = Event.query
    
    # Apply filters
    if status:
        query = query.filter_by(status=status)
    
    if category:
        query = query.filter_by(category=category)
    
    # Order by creation date
    query = query.order_by(Event.created_at.desc())
    
    # Paginate
    pagination = query.paginate(
        page=page,
        per_page=20,
        error_out=False
    )
    
    return render_template(
        'admin/manage_events.html',
        title='Manage Events',
        events=pagination.items,
        pagination=pagination,
        status=status,
        category=category
    )


@admin_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
def edit_event(event_id):
    """
    Edit event details as admin.
    
    Args:
        event_id: ID of the event to edit
    
    Returns:
        Rendered edit form or redirect on success
    """
    # Get event by ID
    event = Event.query.get_or_404(event_id)
    
    # Create form with current event data
    form = AdminEventEditForm(
        title=event.title,
        description=event.description,
        location=event.location,
        event_date=event.event_date,
        registration_deadline=event.registration_deadline,
        capacity=event.capacity,
        category=event.category,
        status=event.status
    )
    
    # Process form submission
    if form.validate_on_submit():
        try:
            # Update event data
            event.title = form.title.data
            event.description = form.description.data
            event.location = form.location.data
            event.event_date = form.event_date.data
            event.registration_deadline = form.registration_deadline.data
            event.capacity = form.capacity.data
            event.category = form.category.data
            event.status = form.status.data
            
            # Save changes
            db.session.commit()
            
            # Flash success message
            flash(f'Event "{event.title}" updated successfully!', 'success')
            
            # Redirect to event management
            return redirect(url_for('admin.manage_events'))
            
        except Exception as e:
            # Rollback on error
            db.session.rollback()
            flash(f'Failed to update event: {str(e)}', 'danger')
    
    # Render edit template
    return render_template('admin/edit_event.html', title='Edit Event', form=form, event=event)


@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
def delete_event(event_id):
    """
    Delete an event as admin.
    
    Args:
        event_id: ID of the event to delete
    
    Returns:
        Redirect to event management
    """
    # Get event by ID
    event = Event.query.get_or_404(event_id)
    
    try:
        # Store event title for flash message
        event_title = event.title
        
        # Delete event (cascades to registrations)
        db.session.delete(event)
        db.session.commit()
        
        # Flash success message
        flash(f'Event "{event_title}" deleted successfully!', 'success')
        
    except Exception as e:
        # Rollback on error
        db.session.rollback()
        flash(f'Failed to delete event: {str(e)}', 'danger')
    
    # Redirect to event management
    return redirect(url_for('admin.manage_events'))


@admin_bp.route('/events/<int:event_id>/registrations')
def event_registrations(event_id):
    """
    View all registrations for a specific event.
    
    Args:
        event_id: ID of the event
    
    Returns:
        Rendered template with registrations
    """
    # Get event by ID
    event = Event.query.get_or_404(event_id)
    
    # Get registrations
    registrations = EventRegistration.query.filter_by(
        event_id=event_id
    ).join(User).order_by(EventRegistration.registration_date.desc()).all()
    
    return render_template(
        'admin/event_registrations.html',
        title=f'Registrations for {event.title}',
        event=event,
        registrations=registrations
    )


@admin_bp.route('/registrations')
def all_registrations():
    """
    Display all event registrations.
    
    Query parameters:
        page: Page number
        event_id: Filter by event
    
    Returns:
        Rendered template with registrations
    """
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    event_id = request.args.get('event_id', type=int)
    
    # Build query
    query = EventRegistration.query
    
    # Filter by event if specified
    if event_id:
        query = query.filter_by(event_id=event_id)
    
    # Order by registration date
    query = query.order_by(EventRegistration.registration_date.desc())
    
    # Paginate
    pagination = query.paginate(
        page=page,
        per_page=20,
        error_out=False
    )
    
    # Get all events for filter dropdown
    events = Event.query.order_by(Event.title).all()
    
    return render_template(
        'admin/all_registrations.html',
        title='All Registrations',
        registrations=pagination.items,
        pagination=pagination,
        events=events,
        selected_event_id=event_id
    )


@admin_bp.route('/promote/<int:user_id>')
def promote_to_organizer(user_id):
    """
    Promote a user to organizer role.
    
    Args:
        user_id: ID of the user to promote
    
    Returns:
        Redirect to user management
    """
    # Get user by ID
    user = User.query.get_or_404(user_id)
    
    try:
        # Update user role
        user.role = 'organizer'
        db.session.commit()
        
        # Flash success message
        flash(f'{user.username} has been promoted to organizer.', 'success')
        
    except Exception as e:
        # Rollback on error
        db.session.rollback()
        flash(f'Failed to promote user: {str(e)}', 'danger')
    
    # Redirect to user management
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/demote/<int:user_id>')
def demote_to_user(user_id):
    """
    Demote an organizer to user role.
    
    Args:
        user_id: ID of the user to demote
    
    Returns:
        Redirect to user management
    """
    # Get user by ID
    user = User.query.get_or_404(user_id)
    
    # Prevent demoting admins
    if user.is_admin():
        flash('Cannot demote admin users.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    try:
        # Update user role
        user.role = 'user'
        db.session.commit()
        
        # Flash success message
        flash(f'{user.username} has been demoted to user.', 'success')
        
    except Exception as e:
        # Rollback on error
        db.session.rollback()
        flash(f'Failed to demote user: {str(e)}', 'danger')
    
    # Redirect to user management
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/statistics')
def statistics():
    """
    Display detailed system statistics.
    
    Returns:
        Rendered statistics template
    """
    # User statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    admin_users = User.query.filter_by(role='admin').count()
    organizer_users = User.query.filter_by(role='organizer').count()
    
    # Event statistics
    total_events = Event.query.count()
    upcoming_events = Event.query.filter(
        Event.event_date > datetime.utcnow()
    ).count()
    past_events = Event.query.filter(
        Event.event_date <= datetime.utcnow()
    ).count()
    
    # Registration statistics
    total_registrations = EventRegistration.query.count()
    cancelled_registrations = EventRegistration.query.filter_by(
        status='cancelled'
    ).count()
    
    # Category breakdown
    category_stats = db.session.query(
        Event.category,
        db.func.count(Event.id)
    ).group_by(Event.category).all()
    
    # Monthly registration stats
    monthly_stats = db.session.query(
        db.func.strftime('%Y-%m', EventRegistration.registration_date),
        db.func.count(EventRegistration.id)
    ).group_by(
        db.func.strftime('%Y-%m', EventRegistration.registration_date)
    ).order_by(
        db.func.strftime('%Y-%m', EventRegistration.registration_date).desc()
    ).limit(12).all()
    
    return render_template(
        'admin/statistics.html',
        title='Statistics',
        total_users=total_users,
        active_users=active_users,
        admin_users=admin_users,
        organizer_users=organizer_users,
        total_events=total_events,
        upcoming_events=upcoming_events,
        past_events=past_events,
        total_registrations=total_registrations,
        cancelled_registrations=cancelled_registrations,
        category_stats=category_stats,
        monthly_stats=monthly_stats
    )
