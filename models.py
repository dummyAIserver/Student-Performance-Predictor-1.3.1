"""
SQLAlchemy Database Models for Student Performance Predictor
Python 3.10 Compatible
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy (will be bound to app in app.py)
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model with role-based access control"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to predictions
    predictions = db.relationship('Prediction', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password: str) -> None:
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role == 'admin'
    
    def is_teacher(self) -> bool:
        """Check if user has teacher role"""
        return self.role == 'teacher'
    
    def is_student(self) -> bool:
        """Check if user has student role"""
        return self.role == 'student'
    
    def can_view_all_predictions(self) -> bool:
        """Teachers and admins can view all predictions"""
        return self.role in ['teacher', 'admin']
    
    def __repr__(self) -> str:
        return f'<User {self.username} ({self.role})>'


class Prediction(db.Model):
    """Prediction history model"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    attendance = db.Column(db.Float, nullable=False)
    assignment_score = db.Column(db.Float, nullable=False)
    internal_marks = db.Column(db.Float, nullable=False)
    predicted_marks = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(2), nullable=False)
    performance = db.Column(db.String(20), nullable=False)
    model_used = db.Column(db.String(50), default='Linear Regression')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key to user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def to_dict(self) -> dict:
        """Convert prediction to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'student_name': self.student_name,
            'attendance': self.attendance,
            'assignment_score': self.assignment_score,
            'internal_marks': self.internal_marks,
            'predicted_marks': self.predicted_marks,
            'prediction': self.predicted_marks,  # For backward compatibility
            'grade': self.grade,
            'performance': self.performance,
            'model_used': self.model_used,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_id': self.user_id
        }
    
    def __repr__(self) -> str:
        return f'<Prediction {self.student_name}: {self.predicted_marks}>'


class ModelMetric(db.Model):
    """Store ML model performance metrics"""
    __tablename__ = 'model_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(50), unique=True, nullable=False)
    r2_score = db.Column(db.Float, nullable=False)
    mae = db.Column(db.Float, nullable=False)  # Mean Absolute Error
    rmse = db.Column(db.Float, nullable=False)  # Root Mean Squared Error
    mape = db.Column(db.Float, nullable=True)  # Mean Absolute Percentage Error
    trained_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert metrics to dictionary"""
        return {
            'id': self.id,
            'name': self.model_name,
            'model_name': self.model_name,
            'r2': self.r2_score,
            'r2_score': self.r2_score,
            'mae': self.mae,
            'rmse': self.rmse,
            'mape': self.mape,
            'trained_at': self.trained_at.isoformat() if self.trained_at else None
        }
    
    def __repr__(self) -> str:
        return f'<ModelMetric {self.model_name}: R²={self.r2_score:.3f}>'


def init_db(app) -> None:
    """Initialize database with Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default admin user if no users exist
        if not User.query.first():
            create_default_users()


def create_default_users() -> None:
    """Create default admin and sample users for testing"""
    # Create admin user
    admin = User(
        username='admin',
        email='admin@example.com',
        role='admin'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Create teacher user
    teacher = User(
        username='teacher',
        email='teacher@example.com',
        role='teacher'
    )
    teacher.set_password('teacher123')
    db.session.add(teacher)
    
    # Create student user
    student = User(
        username='student',
        email='student@example.com',
        role='student'
    )
    student.set_password('student123')
    db.session.add(student)
    
    db.session.commit()
    print("Default users created:")
    print("  Admin: admin / admin123")
    print("  Teacher: teacher / teacher123")
    print("  Student: student / student123")


def get_user_predictions(user_id: int, include_all: bool = False) -> list:
    """
    Get predictions for a user.
    If include_all is True and user is teacher/admin, return all predictions.
    """
    user = User.query.get(user_id)
    if not user:
        return []
    
    if include_all and user.can_view_all_predictions():
        predictions = Prediction.query.order_by(Prediction.created_at.desc()).all()
    else:
        predictions = Prediction.query.filter_by(user_id=user_id).order_by(Prediction.created_at.desc()).all()
    
    return [p.to_dict() for p in predictions]
