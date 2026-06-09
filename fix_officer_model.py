from app.extensions import db 
from datetime import datetime 
 
class Officer(db.Model): 
    __tablename__ = 'officers' 
 
    id = db.Column(db.Integer, primary_key=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) 
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
    reporting_officer_id = db.Column(db.Integer, nullable=True) 
    countersigning_officer_id = db.Column(db.Integer, nullable=True) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 
 
    user = db.relationship('User', backref='officer_profile', uselist=False) 
 
    @property 
    def full_name(self): 
        return f"{self.surname} {self.first_name} {self.other_names or ''}".strip() 
 
    def __repr__(self): 
