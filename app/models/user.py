from app.extensions import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='STAFF')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Staff/Employee personal information
    staff_no = db.Column(db.String(50), unique=True)
    surname = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    other_names = db.Column(db.String(200))
    title = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date, nullable=True)
    date_first_appointment = db.Column(db.Date, nullable=True)
    post_appointed = db.Column(db.String(200))
    present_post = db.Column(db.String(200))
    salary_grade = db.Column(db.String(50))
    
    # Organization fields for workflow routing
    ministry = db.Column(db.String(200))  # MDA
    department = db.Column(db.String(200))  # Department
    division = db.Column(db.String(200))
    branch = db.Column(db.String(200))
    section = db.Column(db.String(200))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role):
        return self.role == role or self.role == 'ADMIN'
    
    @property
    def full_name(self):
        return f"{self.surname} {self.first_name} {self.other_names or ''}".strip()
    
    @property
    def can_assess_reports(self):
        return self.role == 'REPORTING_OFFICER' and self.department is not None
    
    @property
    def can_countersign_reports(self):
        return self.role == 'COUNTERSIGNING_OFFICER' and self.ministry is not None
    
    def to_dict(self):
        """Convert user to dict for audit logging"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'full_name': self.full_name,
            'staff_no': self.staff_no,
            'surname': self.surname,
            'first_name': self.first_name,
            'other_names': self.other_names,
            'title': self.title,
            'ministry': self.ministry,
            'department': self.department,
            'division': self.division,
            'branch': self.branch,
            'section': self.section
        }
    
    def __repr__(self):
        return f'<User {self.username} - {self.full_name}>'