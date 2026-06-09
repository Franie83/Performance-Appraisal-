from app.extensions import db
from datetime import datetime

class Supervision(db.Model):
    __tablename__ = 'supervisions'
    
    id = db.Column(db.Integer, primary_key=True)
    officer_id = db.Column(db.Integer, db.ForeignKey('officers.id'))
    reporting_officer_id = db.Column(db.Integer, db.ForeignKey('officers.id'))
    countersigning_officer_id = db.Column(db.Integer, db.ForeignKey('officers.id'))
    effective_date = db.Column(db.Date, default=datetime.utcnow().date)
    
    officer = db.relationship('Officer', foreign_keys=[officer_id], backref='supervisions')
    reporting_officer = db.relationship('Officer', foreign_keys=[reporting_officer_id])
    countersigning_officer = db.relationship('Officer', foreign_keys=[countersigning_officer_id])