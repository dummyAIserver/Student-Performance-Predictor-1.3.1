"""
Authentication module for Student Performance Predictor
Handles login, registration, and user management
Python 3.10 Compatible
"""

from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import validate_csrf
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db, User, init_db
import re
from urllib.parse import urlparse

# Create Blueprint
auth_bp = Blueprint('auth', __name__)

# Initialize Flask-Login
login_manager = LoginManager()

# Initialize rate limiting
limiter = Limiter(key_func=get_remote_address)


def init_auth(app):
    """Initialize authentication with Flask app"""
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Initialize rate limiting with app
    limiter.init_app(app)
    
    # Register blueprint
    app.register_blueprint(auth_bp, url_prefix='/auth')


@login_manager.user_loader
def load_user(user_id: str):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


def role_required(*allowed_roles):
    """Decorator to require specific roles for access"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role not in allowed_roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('main.home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Rate limit error handler
@auth_bp.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded errors"""
    flash('Too many attempts. Please try again later.', 'warning')
    return redirect(url_for('auth.login'))


# Routes

@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        # Validate CSRF token
        try:
            validate_csrf(request.form.get('csrf_token'))
        except Exception:
            flash('Invalid CSRF token. Please try again.', 'danger')
            return render_template('register.html', 
                                 username=request.form.get('username', ''), 
                                 email=request.form.get('email', ''), 
                                 role=request.form.get('role', 'student'))
        
        username = request.form.get('username', '').strip().lower()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'student')
        
        # Validation
        errors = []
        
        # Basic format validation first
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        elif not username.replace('_', '').isalnum():
            errors.append('Username can only contain letters, numbers, and underscores.')
        
        # Email validation with regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email or not re.match(email_pattern, email):
            errors.append('Please enter a valid email address.')
        
        # Check for duplicates early (before password validation)
        duplicate_errors = []
        if User.query.filter_by(username=username).first():
            duplicate_errors.append('Username already exists.')
        
        if User.query.filter_by(email=email).first():
            duplicate_errors.append('Email already registered.')
        
        # If duplicates exist, show only duplicate errors (skip password validation)
        if duplicate_errors:
            errors.extend(duplicate_errors)
        else:
            # Only validate password if no duplicates (user is actually trying to register)
            if not password or len(password) < 6:
                errors.append('Password must be at least 6 characters.')
            elif not re.search(r'[A-Z]', password):
                errors.append('Password must contain at least one uppercase letter.')
            elif not re.search(r'[a-z]', password):
                errors.append('Password must contain at least one lowercase letter.')
            elif not re.search(r'\d', password):
                errors.append('Password must contain at least one number.')
            elif not re.search(r'[!@#$%^&*()_+=\-\[\]{}|;:\'",.<>?/~`]', password):
                errors.append('Password must contain at least one special character.')
            
            if password != confirm_password:
                errors.append('Passwords do not match.')
        
        # Validate role (only admin can create teachers/admins)
        if role not in ['student', 'teacher', 'admin']:
            role = 'student'
        
        # If trying to register as teacher/admin, check if admin exists and allow first admin
        if role in ['teacher', 'admin']:
            admin_exists = User.query.filter_by(role='admin').first()
            if admin_exists and (not current_user.is_authenticated or not current_user.is_admin()):
                errors.append('Only admins can create teacher or admin accounts.')
                role = 'student'
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html', 
                                 username=username, 
                                 email=email, 
                                 role=role)
        
        # Create user
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        # Validate CSRF token
        try:
            validate_csrf(request.form.get('csrf_token'))
        except Exception:
            flash('Invalid CSRF token. Please try again.', 'danger')
            return render_template('login.html')
        
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        # Find user by username (case-insensitive) or email
        user = User.query.filter(
            db.or_(db.func.lower(User.username) == username, User.email == username)
        ).first()
        
        if user and user.check_password(password):
            login_user(user, remember=bool(remember))
            
            # Get next page from query string
            next_page = request.args.get('next')
            if next_page:
                # Only allow relative URLs within our site to prevent open redirect attacks
                parsed = urlparse(next_page)
                if not parsed.netloc and parsed.path.startswith('/'):
                    return redirect(next_page)
            
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('main.home'))
        else:
            # Timing-safe password verification to prevent user enumeration
            # Always perform password check to prevent timing attacks
            from werkzeug.security import check_password_hash
            check_password_hash('dummy_hash', password)
            
            # Use same error message for both cases to prevent user enumeration
            flash('Invalid username/email or password.', 'danger')
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    # Get user's prediction count
    prediction_count = len(current_user.predictions)
    
    return render_template('profile.html', 
                        user=current_user,
                        prediction_count=prediction_count)


@auth_bp.route('/profile/edit', methods=['POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    email = request.form.get('email', '').strip().lower()
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    
    errors = []
    
    # Validate email
    if email and email != current_user.email:
        if '@' not in email:
            errors.append('Please enter a valid email address.')
        elif User.query.filter_by(email=email).first():
            errors.append('Email already registered by another user.')
        else:
            current_user.email = email
    
    # Change password if requested
    if new_password:
        if not current_password:
            errors.append('Current password is required to change password.')
        elif not current_user.check_password(current_password):
            errors.append('Current password is incorrect.')
        elif len(new_password) < 6:
            errors.append('New password must be at least 6 characters.')
        else:
            current_user.set_password(new_password)
    
    if errors:
        for error in errors:
            flash(error, 'danger')
    else:
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    
    return redirect(url_for('auth.profile'))


# Admin routes

@auth_bp.route('/admin/users')
@login_required
@role_required('admin')
def admin_users():
    """Admin: View all users"""
    users = User.query.all()
    return render_template('admin_users.html', users=users)


@auth_bp.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete_user(user_id: int):
    """Admin: Delete a user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('auth.admin_users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} has been deleted.', 'success')
    return redirect(url_for('auth.admin_users'))


@auth_bp.route('/admin/user/<int:user_id>/role', methods=['POST'])
@login_required
@role_required('admin')
def admin_change_role(user_id: int):
    """Admin: Change user role"""
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role', 'student')
    
    if new_role not in ['student', 'teacher', 'admin']:
        flash('Invalid role.', 'danger')
        return redirect(url_for('auth.admin_users'))
    
    # Prevent admin from demoting themselves
    if user.id == current_user.id and new_role != 'admin':
        flash('You cannot remove your own admin privileges.', 'danger')
        return redirect(url_for('auth.admin_users'))
    
    user.role = new_role
    db.session.commit()
    
    flash(f'{user.username} is now a {new_role}.', 'success')
    return redirect(url_for('auth.admin_users'))


@auth_bp.route('/check-username')
def check_username():
    """AJAX endpoint to check username availability"""
    username = request.args.get('username', '').strip().lower()
    if not username:
        return jsonify({'available': False, 'message': 'Username is required'})
    
    existing = User.query.filter(db.func.lower(User.username) == username).first()
    if existing:
        return jsonify({'available': False, 'message': 'Username already taken'})
    
    return jsonify({'available': True, 'message': 'Username available'})


@auth_bp.route('/check-email')
def check_email():
    """AJAX endpoint to check email availability"""
    email = request.args.get('email', '').strip().lower()
    if not email:
        return jsonify({'available': False, 'message': 'Email is required'})
    
    # Email format validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return jsonify({'available': False, 'message': 'Invalid email format'})
    
    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({'available': False, 'message': 'Email already registered'})
    
    return jsonify({'available': True, 'message': 'Email available'})
