"""
Event routes for CRUD operations on events.
Handles event listing, creation, viewing, editing, and registration.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from forms import EventForm, SearchForm
from models import Event, EventRegistration, User, Category, Tag, db
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename


# Create events blueprint
events_bp = Blueprint('events', __name__, url_prefix='/events')


def allowed_file(filename):
    """
    Check if uploaded file has an allowed extension.
    
    Args:
        filename: Name of the uploaded file
    
    Returns:
        Boolean indicating if file is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@events_bp.route('/')
def index():
    """
    Display all upcoming published events.
    
    Query parameters:
        page: Page number for pagination
        category: Filter by category
        search: Search query
        location: Filter by location
        date_from: Filter events from this date
        date_to: Filter events until this date
    
    Returns:
        Rendered event list template
    """
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    location = request.args.get('location', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Build base query for published, upcoming events
    query = Event.query.filter(
        Event.status == 'published',
        Event.event_date > datetime.utcnow()
    )
    
    # Apply filters
    if category:
        query = query.filter(Event.category == category)
    
    if search:
        query = query.filter(
            (Event.title.ilike(f'%{search}%')) |
            (Event.description.ilike(f'%{search}%'))
        )
    
    if location:
        query = query.filter(Event.location.ilike(f'%{location}%'))
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Event.event_date >= date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(Event.event_date <= date_to_obj)
        except ValueError:
            pass
    
    # Order by event date
    query = query.order_by(Event.event_date.asc())
    
    # Paginate results
    pagination = query.paginate(
        page=page,
        per_page=current_app.config.get('ITEMS_PER_PAGE', 10),
        error_out=False
    )
    
    # Get categories for filter dropdown
    categories = Category.query.all()
    
    # Calculate quick filter dates
    today = datetime.utcnow().strftime('%Y-%m-%d')
    week_start = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d')
    week_end = (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d')
    month_start = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d')
    month_end = (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    return render_template(
        'events/event_list.html',
        title='Upcoming Events',
        events=pagination.items,
        pagination=pagination,
        category=category,
        search=search,
        location=location,
        date_from=date_from,
        date_to=date_to,
        categories=categories,
        today=today,
        week_start=week_start,
        week_end=week_end,
        month_start=month_start,
        month_end=month_end
    )


@events_bp.route('/calendar')
def calendar():
    """
    Display events in calendar view.
    
    Query parameters:
        year: Year to display
        month: Month to display
    
    Returns:
        Rendered calendar template
    """
    # Get year and month from query params or use current date
    now = datetime.utcnow()
    year = request.args.get('year', now.year, type=int)
    month = request.args.get('month', now.month, type=int)
    
    # Get first day of the month
    first_day = datetime(year, month, 1)
    
    # Get last day of the month
    if month == 12:
        last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1) - timedelta(days=1)
    
    # Get events for this month
    events = Event.query.filter(
        Event.status == 'published',
        Event.event_date >= first_day,
        Event.event_date <= last_day
    ).order_by(Event.event_date).all()
    
    # Group events by date
    events_by_date = {}
    for event in events:
        date_key = event.event_date.strftime('%Y-%m-%d')
        if date_key not in events_by_date:
            events_by_date[date_key] = []
        events_by_date[date_key].append(event)
    
    # Get previous and next month
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    # Month name
    month_name = first_day.strftime('%B %Y')
    
    # Get current datetime for today comparison
    now = datetime.utcnow()
    
    return render_template(
        'events/calendar.html',
        title='Event Calendar',
        events_by_date=events_by_date,
        year=year,
        month=month,
        month_name=month_name,
        prev_year=prev_year,
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month,
        first_day=first_day,
        last_day=last_day,
        now=now
    )


@events_bp.route('/my-events')
@login_required
def my_events():
    """
    Display events created by the current user.
    
    Returns:
        Rendered template with user's events
    """
    # Get user's events
    events = Event.query.filter_by(creator_id=current_user.id)\
        .order_by(Event.created_at.desc())\
        .all()
    
    return render_template(
        'events/my_events.html',
        title='My Events',
        events=events
    )


@events_bp.route('/registered')
@login_required
def registered_events():
    """
    Display events the current user is registered for.
    
    Returns:
        Rendered template with registered events
    """
    # Get user's registrations
    registrations = EventRegistration.query.filter_by(
        user_id=current_user.id,
        status='registered'
    ).join(Event).order_by(Event.event_date.asc()).all()
    
    return render_template(
        'events/registered_events.html',
        title='Registered Events',
        registrations=registrations
    )


@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    """
    Create a new event.
    
    GET: Display event creation form
    POST: Process event creation
    
    Returns:
        Rendered form or redirect to event detail on success
    """
    # Check if user can create events
    if not current_user.is_organizer():
        flash('You do not have permission to create events.', 'warning')
        return redirect(url_for('main.home'))
    
    # Create event form
    form = EventForm()
    
    # Process form submission
    if form.validate_on_submit():
        try:
            # Get uploaded file
            file = request.files.get('image')
            filename = None
            
            if file and allowed_file(file.filename):
                # Secure filename and save
                filename = secure_filename(file.filename)
                file.save(os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    filename
                ))
            
            # Create new event
            event = Event(
                title=form.title.data,
                description=form.description.data,
                location=form.location.data,
                event_date=form.event_date.data,
                registration_deadline=form.registration_deadline.data,
                capacity=form.capacity.data,
                category=form.category.data,
                status=form.status.data,
                image_filename=filename,
                creator_id=current_user.id
            )
            
            # Add event to database
            db.session.add(event)
            db.session.commit()
            
            # Flash success message
            flash('Event created successfully!', 'success')
            
            # Redirect to event detail
            return redirect(url_for('events.event_detail', event_id=event.id))
            
        except Exception as e:
            # Rollback on error
            db.session.rollback()
            flash(f'Failed to create event: {str(e)}', 'danger')
    
    # Render event creation template
    return render_template('events/create_event.html', title='Create Event', form=form)


@events_bp.route('/<int:event_id>')
def event_detail(event_id):
    """
    Display event details.
    
    Args:
        event_id: ID of the event to display
    
    Returns:
        Rendered event detail template or 404 if not found
    """
    # Get event by ID
    event = Event.query.get_or_404(event_id)
    
    # Check if user is registered
    is_registered = False
    if current_user.is_authenticated:
        is_registered = event.is_user_registered(current_user.id)
    
    # Get registration count
    registration_count = event.get_registration_count()
    
    return render_template(
        'events/event_detail.html',
        title=event.title,
        event=event,
        is_registered=is_registered,
        registration_count=registration_count
    )


@events_bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    """
    Edit an existing event.
    
    Args:
        event_id: ID of the event to edit
    
    Returns:
        Rendered edit form or redirect on success
    """
    # Get event by ID
    event = Event.query.get_or_404(event_id)
    
    # Check if user can edit (creator or admin)
    if event.creator_id != current_user.id and not current_user.is_admin():
        abort(403)
    
    # Create form with current event data
    form = EventForm(
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
            # Get uploaded file
            file = request.files.get('image')
            filename = event.image_filename
            
            if file and allowed_file(file.filename):
                # Secure filename and save
                filename = secure_filename(file.filename)
                file.save(os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    filename
                ))
            
            # Update event data
            event.title = form.title.data
            event.description = form.description.data
            event.location = form.location.data
            event.event_date = form.event_date.data
            event.registration_deadline = form.registration_deadline.data
            event.capacity = form.capacity.data
            event.category = form.category.data
            event.status = form.status.data
            event.image_filename = filename
            
            # Save changes
            db.session.commit()
            
            # Flash success message
            flash('Event updated successfully!', 'success')
            
            # Redirect to event detail
            return redirect(url_for('events.event_detail', event_id=event.id))
            
        except Exception as e:
            # Rollback on error
            db.session.rollback()
            flash(f'Failed to update event: {str(e)}', 'danger')
    
    # Render event edit template
    return render_template('events/edit_event.html', title='Edit Event', form=form, event=event)


@events_bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    """
    Delete an event.
    
    Args:
        event_id: ID of the event to delete
    
    Returns:
        Redirect to events list on success
    """
    # Get event by ID
    event = Event.query.get_or_404(event_id)
    
    # Check if user can delete (creator or admin)
    if event.creator_id != current_user.id and not current_user.is_admin():
        abort(403)
    
    try:
        # Delete event (cascades to registrations)
        db.session.delete(event)
        db.session.commit()
        
        # Flash success message
        flash('Event deleted successfully!', 'success')
        
    except Exception as e:
        # Rollback on error
        db.session.rollback()
        flash(f'Failed to delete event: {str(e)}', 'danger')
    
    # Redirect to events list
    return redirect(url_for('events.my_events'))


@events_bp.route('/<int:event_id>/register', methods=['POST'])
@login_required
def register_for_event(event_id):
    """
    Register current user for an event.
    
    Args:
        event_id: ID of the event to register for
    
    Returns:
        Redirect to event detail with status message
    """
    # Get event by ID
    event = Event.query.get_or_404(event_id)
    
    # Check if registration is open
    if not event.is_registration_open:
        flash('Registration for this event is closed.', 'warning')
        return redirect(url_for('events.event_detail', event_id=event.id))
    
    # Check if event is full
    if event.is_full:
        flash('This event is fully booked.', 'warning')
        return redirect(url_for('events.event_detail', event_id=event.id))
    
    # Check if already registered
    if event.is_user_registered(current_user.id):
        flash('You are already registered for this event.', 'info')
        return redirect(url_for('events.event_detail', event_id=event.id))
    
    # Check if user is the creator
    if event.creator_id == current_user.id:
        flash('You cannot register for your own event.', 'warning')
        return redirect(url_for('events.event_detail', event_id=event.id))
    
    try:
        # Create registration
        registration = EventRegistration(
            user_id=current_user.id,
            event_id=event.id,
            status='registered'
        )
        
        # Add registration to database
        db.session.add(registration)
        db.session.commit()
        
        # Flash success message
        flash(f'Successfully registered for {event.title}!', 'success')
        
    except Exception as e:
        # Rollback on error
        db.session.rollback()
        flash(f'Failed to register for event: {str(e)}', 'danger')
    
    # Redirect to event detail
    return redirect(url_for('events.event_detail', event_id=event.id))


@events_bp.route('/<int:event_id>/unregister', methods=['POST'])
@login_required
def unregister_from_event(event_id):
    """
    Unregister current user from an event.
    
    Args:
        event_id: ID of the event to unregister from
    
    Returns:
        Redirect to event detail with status message
    """
    # Get event by ID
    event = Event.query.get_or_404(event_id)
    
    # Find user's registration
    registration = EventRegistration.query.filter_by(
        user_id=current_user.id,
        event_id=event_id
    ).first()
    
    if not registration:
        flash('You are not registered for this event.', 'warning')
        return redirect(url_for('events.event_detail', event_id=event.id))
    
    try:
        # Delete registration
        db.session.delete(registration)
        db.session.commit()
        
        # Flash success message
        flash(f'Successfully unregistered from {event.title}.', 'success')
        
    except Exception as e:
        # Rollback on error
        db.session.rollback()
        flash(f'Failed to unregister from event: {str(e)}', 'danger')
    
    # Redirect to event detail
    return redirect(url_for('events.event_detail', event_id=event.id))
