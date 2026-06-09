from app.extensions import db
from datetime import datetime

class Countersignature(db.Model):
    __tablename__ = 'countersignatures'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('performance_reports.id'))
    
    # Section 13: Countersigning Officer's Report
    agrees_with_assessment = db.Column(db.Boolean, default=True)
    disagreements = db.Column(db.Text)
    frequency_seen_work = db.Column(db.String(100))  # Daily, Weekly, Monthly, etc.
    additional_comments = db.Column(db.Text)
    adverse_comments_brought_to_attention = db.Column(db.Boolean, default=False)
    
    # Service under countersigning officer
    years_served_under = db.Column(db.Numeric(4, 1))
    months_served_under = db.Column(db.Integer)
    
    # Countersigning Officer details
    countersigning_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    signature = db.Column(db.String(500))
    name_block = db.Column(db.String(200))
    post_held = db.Column(db.String(200))
    grade_level = db.Column(db.String(50))
    date_signed = db.Column(db.Date)
    
    report = db.relationship('PerformanceReport', backref='countersignature')
    countersigning_officer = db.relationship('User', foreign_keys=[countersigning_officer_id])
    
    def __repr__(self):
        return f'<Countersignature Report {self.report_id}>'