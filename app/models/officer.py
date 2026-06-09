from app.extensions import db
from datetime import datetime

class Officer(db.Model):
    __tablename__ = 'officers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    staff_no = db.Column(db.String(50), unique=True)
    surname = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    other_names = db.Column(db.String(200))
    title = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    date_first_appointment = db.Column(db.Date)
    post_appointed = db.Column(db.String(200))
    present_post = db.Column(db.String(200))
    salary_grade = db.Column(db.String(50))
    ministry = db.Column(db.String(200))
    department = db.Column(db.String(200))
    division = db.Column(db.String(200))
    branch = db.Column(db.String(200))
    section = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add the relationship to User
    user = db.relationship('User', backref='officer_profile', uselist=False, foreign_keys=[user_id])
    
    @property
    def full_name(self):
        if self.surname and self.first_name:
            return f"{self.title or ''} {self.surname} {self.first_name}".strip()
        elif self.surname:
            return self.surname
        else:
            return "Unknown"
    
    def __repr__(self):
        return f'<Officer {self.staff_no}: {self.full_name}>'