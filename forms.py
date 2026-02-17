"""
WTForms for the Event Management System.
Defines all form classes for user input validation.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateTimeField, \
    IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from models import User


class RegistrationForm(FlaskForm):
    """
    User registration form with validation.
    
    Fields:
        username: Unique username
        email: Unique email address
        password: Secure password
        confirm_password: Password confirmation
        first_name: Optional first name
        last_name: Optional last name
        submit: Registration button
    """
    
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email must be less than 120 characters')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, max=100, message='Password must be at least 6 characters')
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    
    first_name = StringField('First Name', validators=[
        Optional(),
        Length(max=50, message='First name must be less than 50 characters')
    ])
    
    last_name = StringField('Last Name', validators=[
        Optional(),
        Length(max=50, message='Last name must be less than 50 characters')
    ])
    
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """
        Check if username already exists in database.
        
        Args:
            username: Username field to validate
        
        Raises:
            ValidationError: If username is already taken
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """
        Check if email already exists in database.
        
        Args:
            email: Email field to validate
        
        Raises:
            ValidationError: If email is already registered
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use a different one.')


class LoginForm(FlaskForm):
    """
    User login form with validation.
    
    Fields:
        email_or_username: Email or username for login
        password: User password
        remember: Remember me checkbox
        submit: Login button
    """
    
    email_or_username = StringField('Email or Username', validators=[
        DataRequired(message='Please enter your email or username'),
        Length(max=120, message='Input must be less than 120 characters')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    
    remember = BooleanField('Remember Me')
    
    submit = SubmitField('Login')


class UpdateProfileForm(FlaskForm):
    """
    User profile update form.
    
    Fields:
        username: Unique username
        email: Unique email address
        first_name: Optional first name
        last_name: Optional last name
        submit: Update button
    """
    
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email must be less than 120 characters')
    ])
    
    first_name = StringField('First Name', validators=[
        Optional(),
        Length(max=50, message='First name must be less than 50 characters')
    ])
    
    last_name = StringField('Last Name', validators=[
        Optional(),
        Length(max=50, message='Last name must be less than 50 characters')
    ])
    
    submit = SubmitField('Update Profile')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        """
        Initialize form with original values to exclude current user from validation.
        
        Args:
            original_username: Current username of user
            original_email: Current email of user
        """
        super().__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
    
    def validate_username(self, username):
        """Validate username is unique except for current user."""
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """Validate email is unique except for current user."""
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email is already registered. Please use a different one.')


class ChangePasswordForm(FlaskForm):
    """
    Password change form.
    
    Fields:
        old_password: Current password
        new_password: New password
        confirm_new_password: Confirm new password
        submit: Change password button
    """
    
    old_password = PasswordField('Current Password', validators=[
        DataRequired(message='Please enter your current password')
    ])
    
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='Please enter a new password'),
        Length(min=6, max=100, message='Password must be at least 6 characters')
    ])
    
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password'),
        EqualTo('new_password', message='Passwords must match')
    ])
    
    submit = SubmitField('Change Password')


class EventForm(FlaskForm):
    """
    Event creation and update form.
    
    Fields:
        title: Event title
        description: Event description
        location: Event location
        event_date: Date and time of event
        registration_deadline: Registration deadline
        capacity: Maximum attendees
        category: Event category
        status: Event status
        submit: Create/Update button
    """
    
    title = StringField('Event Title', validators=[
        DataRequired(message='Event title is required'),
        Length(max=200, message='Title must be less than 200 characters')
    ])
    
    description = TextAreaField('Description', validators=[
        DataRequired(message='Event description is required'),
        Length(min=20, message='Description must be at least 20 characters')
    ])
    
    location = StringField('Location', validators=[
        DataRequired(message='Event location is required'),
        Length(max=255, message='Location must be less than 255 characters')
    ])
    
    event_date = DateTimeField('Event Date & Time', format='%Y-%m-%dT%H:%M', validators=[
        DataRequired(message='Event date and time is required')
    ])
    
    registration_deadline = DateTimeField('Registration Deadline', format='%Y-%m-%dT%H:%M', validators=[
        Optional()
    ])
    
    capacity = IntegerField('Capacity', validators=[
        DataRequired(message='Please specify event capacity'),
    ], default=100)
    
    category = SelectField('Category', choices=[
        ('', 'Select Category'),
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('meetup', 'Meetup'),
        ('social', 'Social'),
        ('sports', 'Sports'),
        ('cultural', 'Cultural'),
        ('educational', 'Educational'),
        ('other', 'Other')
    ], validators=[DataRequired(message='Please select a category')])
    
    status = SelectField('Status', choices=[
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled')
    ], validators=[DataRequired()], default='draft')
    
    submit = SubmitField('Create Event')
    
    def validate_event_date(self, event_date):
        """Ensure event date is in the future."""
        from datetime import datetime
        if event_date.data <= datetime.utcnow():
            raise ValidationError('Event date must be in the future.')
    
    def validate_registration_deadline(self, registration_deadline):
        """Ensure registration deadline is before event date."""
        if registration_deadline.data and self.event_date.data:
            if registration_deadline.data >= self.event_date.data:
                raise ValidationError('Registration deadline must be before the event date.')


class SearchForm(FlaskForm):
    """
    Event search form.
    
    Fields:
        search: Search query
        category: Category filter
        location: Location filter
        submit: Search button
    """
    
    search = StringField('Search', validators=[
        Optional(),
        Length(max=200, message='Search query must be less than 200 characters')
    ])
    
    category = SelectField('Category', choices=[
        ('', 'All Categories'),
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('meetup', 'Meetup'),
        ('social', 'Social'),
        ('sports', 'Sports'),
        ('cultural', 'Cultural'),
        ('educational', 'Educational'),
        ('other', 'Other')
    ], validators=[Optional()])
    
    location = StringField('Location', validators=[
        Optional(),
        Length(max=255, message='Location must be less than 255 characters')
    ])
    
    submit = SubmitField('Search')


class AdminUserEditForm(FlaskForm):
    """
    Admin user editing form.
    
    Fields:
        username: User's username
        email: User's email
        role: User role
        is_active: Account active status
        submit: Update button
    """
    
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email must be less than 120 characters')
    ])
    
    role = SelectField('Role', choices=[
        ('user', 'User'),
        ('organizer', 'Organizer'),
        ('admin', 'Admin')
    ], validators=[DataRequired()])
    
    is_active = BooleanField('Active Account')
    
    submit = SubmitField('Update User')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        """Initialize form with original values."""
        super().__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
    
    def validate_username(self, username):
        """Validate username uniqueness excluding current user."""
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username is already taken.')
    
    def validate_email(self, email):
        """Validate email uniqueness excluding current user."""
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email is already registered.')


class AdminEventEditForm(FlaskForm):
    """
    Admin event editing form.
    
    Fields:
        title: Event title
        description: Event description
        location: Event location
        event_date: Event date and time
        registration_deadline: Registration deadline
        capacity: Event capacity
        category: Event category
        status: Event status
        submit: Update button
    """
    
    title = StringField('Event Title', validators=[
        DataRequired(message='Event title is required'),
        Length(max=200, message='Title must be less than 200 characters')
    ])
    
    description = TextAreaField('Description', validators=[
        DataRequired(message='Event description is required'),
        Length(min=20, message='Description must be at least 20 characters')
    ])
    
    location = StringField('Location', validators=[
        DataRequired(message='Event location is required'),
        Length(max=255, message='Location must be less than 255 characters')
    ])
    
    event_date = DateTimeField('Event Date & Time', format='%Y-%m-%dT%H:%M', validators=[
        DataRequired(message='Event date and time is required')
    ])
    
    registration_deadline = DateTimeField('Registration Deadline', format='%Y-%m-%dT%H:%M', validators=[
        Optional()
    ])
    
    capacity = IntegerField('Capacity', validators=[
        DataRequired(message='Please specify event capacity')
    ])
    
    category = SelectField('Category', choices=[
        ('', 'Select Category'),
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('meetup', 'Meetup'),
        ('social', 'Social'),
        ('sports', 'Sports'),
        ('cultural', 'Cultural'),
        ('educational', 'Educational'),
        ('other', 'Other')
    ], validators=[DataRequired(message='Please select a category')])
    
    status = SelectField('Status', choices=[
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Update Event')
