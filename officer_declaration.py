from app.extensions import db
from datetime import datetime

class OfficerDeclaration(db.Model):
    __tablename__ = 'officer_declarations'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('performance_reports.id'))
    
    # Section 11: Officer's comments
    seen_contents = db.Column(db.Boolean, default=False)
    discussed_with_reporting = db.Column(db.Boolean, default=False)
    officer_comments = db.Column(db.Text)
    declaration_date = db.Column(db.Date)
    officer_signature = db.Column(db.String(500))
    
    report = db.relationship('PerformanceReport', backref='officer_declaration')
    
    def __repr__(self):
        return f'<OfficerDeclaration Report {self.report_id}>'