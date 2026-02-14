"""
Database models for the Event Management System.
Defines Users, Events, and EventRegistrations tables with relationships.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db, login_manager


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


class User(db.Model, UserMixin):
    """
    User model representing registered users in the system.
    
    Attributes:
        id: Unique user identifier
        username: Unique username for login
        email: Unique email address
        password_hash: Hashed password for security
        first_name: User's first name
        last_name: User's last name
        role: User role (user, admin, organizer)
        created_at: Account creation timestamp
        updated_at: Last profile update timestamp
        is_active: Account active status
    """
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(20), default='user', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    events_created = db.relationship('Event', backref='creator', lazy='dynamic', 
                                     foreign_keys='Event.creator_id')
    registrations = db.relationship('EventRegistration', backref='registrant', 
                                    lazy='dynamic', foreign_keys='EventRegistration.user_id', overlaps="event_registrations,user")
    
    def __repr__(self):
        """String representation of User object."""
        return f'<User {self.username}>'
    
    @property
    def full_name(self):
        """Return user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def password(self):
        """Prevent password from being accessed."""
        raise AttributeError('Password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        """Set password by hashing it."""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """Check if provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'admin'
    
    def is_organizer(self):
        """Check if user has organizer role."""
        return self.role in ['admin', 'organizer']
    
    def get_registration_count(self):
        """Get total number of event registrations."""
        return self.registrations.count()
    
    def get_created_events_count(self):
        """Get total number of events created by user."""
        return self.events_created.count()
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }


class Event(db.Model):
    """
    Event model representing events in the system.
    
    Attributes:
        id: Unique event identifier
        title: Event title/name
        description: Detailed event description
        location: Event venue/online location
        event_date: Date and time of event
        registration_deadline: Last date for registration
        capacity: Maximum number of attendees
        image_filename: Event banner image filename
        status: Event status (draft, published, cancelled, completed)
        category: Event category
        creator_id: Foreign key to User who created the event
        created_at: Event creation timestamp
        updated_at: Last event update timestamp
    """
    
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False, index=True)
    registration_deadline = db.Column(db.DateTime, nullable=True)
    capacity = db.Column(db.Integer, default=100, nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='draft', nullable=False)
    category = db.Column(db.String(50), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    registrations = db.relationship('EventRegistration', backref='event', 
                                    lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        """String representation of Event object."""
        return f'<Event {self.title}>'
    
    @property
    def is_upcoming(self):
        """Check if event is in the future."""
        return self.event_date > datetime.utcnow()
    
    @property
    def is_registration_open(self):
        """Check if registration is still open."""
        if self.registration_deadline:
            return datetime.utcnow() < self.registration_deadline and self.status == 'published'
        return self.status == 'published'
    
    @property
    def available_spots(self):
        """Calculate available registration spots."""
        registered = self.registrations.count()
        return max(0, self.capacity - registered)
    
    @property
    def is_full(self):
        """Check if event is at capacity."""
        return self.available_spots <= 0
    
    def get_registration_count(self):
        """Get current registration count."""
        return self.registrations.count()
    
    def get_attendees(self):
        """Get list of registered users."""
        return [reg.user for reg in self.registrations.all()]
    
    def is_user_registered(self, user_id):
        """Check if specific user is registered."""
        return self.registrations.filter_by(user_id=user_id).first() is not None
    
    def to_dict(self):
        """Convert event to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'event_date': self.event_date.isoformat(),
            'registration_deadline': self.registration_deadline.isoformat() if self.registration_deadline else None,
            'capacity': self.capacity,
            'status': self.status,
            'category': self.category,
            'creator_id': self.creator_id,
            'created_at': self.created_at.isoformat()
        }


class EventRegistration(db.Model):
    """
    EventRegistration model for tracking event registrations.
    
    Attributes:
        id: Unique registration identifier
        user_id: Foreign key to User
        event_id: Foreign key to Event
        registration_date: Date of registration
        status: Registration status (registered, cancelled, attended)
        notes: Optional notes from registrant
    """
    
    __tablename__ = 'event_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False, index=True)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default='registered', nullable=False)
    notes = db.Column(db.Text, nullable=True)
    
    # Unique constraint to prevent duplicate registrations
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='_user_event_uc'),)
    
    # Relationships
    user = db.relationship('User', backref='event_registrations', 
                          foreign_keys=[user_id], overlaps="registrant,registrations")
    
    def __repr__(self):
        """String representation of EventRegistration object."""
        return f'<Registration {self.user_id} - {self.event_id}>'
    
    def to_dict(self):
        """Convert registration to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'event_id': self.event_id,
            'registration_date': self.registration_date.isoformat(),
            'status': self.status
        }


class Category(db.Model):
    """
    Category model for organizing events.
    
    Attributes:
        id: Unique category identifier
        name: Category name
        slug: URL-friendly category slug
        description: Category description
        icon: Font Awesome icon class
        color: Bootstrap color class
    """
    
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    icon = db.Column(db.String(50), default='fa-calendar')
    color = db.Column(db.String(20), default='primary')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship - removed problematic backref that requires FK
    pass
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    @staticmethod
    def get_all_categories():
        """Get all categories ordered by name."""
        return Category.query.order_by(Category.name).all()


class Tag(db.Model):
    """
    Tag model for tagging events with keywords.
    
    Attributes:
        id: Unique tag identifier
        name: Tag name
        slug: URL-friendly tag slug
    """
    
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    
    # Relationship
    events = db.relationship('Event', secondary='event_tags', backref='tags')
    
    def __repr__(self):
        return f'<Tag {self.name}>'


class EventTag(db.Model):
    """
    Association table for Event-Tag many-to-many relationship.
    """
    
    __tablename__ = 'event_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)


class Notification(db.Model):
    """
    Notification model for user notifications.
    
    Attributes:
        id: Unique notification identifier
        user_id: Foreign key to User
        title: Notification title
        message: Notification message
        type: Notification type (info, success, warning, danger)
        is_read: Read status
        created_at: Creation timestamp
    """
    
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=True)
    notification_type = db.Column(db.String(20), default='info')
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    user = db.relationship('User', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.id} for User {self.user_id}>'
    
    @staticmethod
    def create_notification(user_id, title, message, notification_type='info'):
        """Create a new notification for a user."""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    
    def mark_as_read(self):
        """Mark notification as read."""
        self.is_read = True
        db.session.commit()
    
    def to_dict(self):
        """Convert notification to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.notification_type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }
