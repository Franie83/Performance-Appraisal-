from app.extensions import db
from datetime import datetime

class Assessment(db.Model):
    __tablename__ = 'assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('performance_reports.id'))
    
    # Section 6: Performance Grading (A=6, B=5, C=4, D=3, E=2, F=1)
    foresight = db.Column(db.String(1))      # (i) Foresight
    judgement = db.Column(db.String(1))       # (ii) Judgement
    oral_expression = db.Column(db.String(1)) # (iii) Oral expression
    relations = db.Column(db.String(1))       # (iv) Relations with colleagues
    punctuality = db.Column(db.String(1))     # (v) Punctuality
    attendance = db.Column(db.String(1))      # (vi) Attendance at work
    industry = db.Column(db.String(1))        # (vii) Industry
    output_work = db.Column(db.String(1))     # (viii) Output of work
    quality_work = db.Column(db.String(1))    # (ix) Quality of Work
    honesty = db.Column(db.String(1))         # (x) Honesty
    
    # Section 7: General remarks
    general_remarks = db.Column(db.Text)
    
    # Section 8: Training recommended
    training_recommended = db.Column(db.Text)
    training_reasons = db.Column(db.Text)
    
    # Service duration under reporting officer (Section 9)
    years_under_supervisor = db.Column(db.Numeric(4, 1))
    months_under_supervisor = db.Column(db.Integer)
    
    # Section 10: Promotability
    promotability_rating = db.Column(db.String(2))  # A, B, C, D, E, F
    promotability_reasons = db.Column(db.Text)
    accelerated_promotion_recommendation = db.Column(db.Text)
    accelerated_promotion_grade = db.Column(db.String(50))
    
    # Workflow Assessment Type
    assessment_type = db.Column(db.String(20), default='REPORTING')  # REPORTING, COUNTERSIGNING
    
    # Reporting Officer details (Section 12)
    reporting_officer_signature = db.Column(db.String(500))
    reporting_officer_name_block = db.Column(db.String(200))
    reporting_officer_post_held = db.Column(db.String(200))
    reporting_officer_grade_level = db.Column(db.String(50))
    reporting_officer_signature_date = db.Column(db.Date)
    
    # Countersigning Officer details
    countersigning_officer_signature = db.Column(db.String(500))
    countersigning_officer_name_block = db.Column(db.String(200))
    countersigning_officer_post_held = db.Column(db.String(200))
    countersigning_officer_grade_level = db.Column(db.String(50))
    countersigning_officer_signature_date = db.Column(db.Date)
    countersigning_comments = db.Column(db.Text)
    
    # Metadata
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    countersigner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    review_date = db.Column(db.DateTime, default=datetime.utcnow)
    countersign_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships - Fixed with overlaps parameter to silence warning
    # The overlaps parameter tells SQLAlchemy that this relationship overlaps with 
    # 'assessment' and 'assessments' from PerformanceReport model
    report = db.relationship('PerformanceReport', backref=db.backref('assessments', cascade='all, delete-orphan'),
                            foreign_keys=[report_id], overlaps='assessment,performance_report')
    
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='assessments_made')
    countersigner = db.relationship('User', foreign_keys=[countersigner_id], backref='assessments_countersigned')
    
    GRADE_WEIGHTS = {'A': 6, 'B': 5, 'C': 4, 'D': 3, 'E': 2, 'F': 1}
    
    def calculate_total_score(self):
        """Calculate total score as percentage"""
        competencies = [self.foresight, self.judgement, self.oral_expression,
                       self.relations, self.punctuality, self.attendance,
                       self.industry, self.output_work, self.quality_work, self.honesty]
        total = sum(self.GRADE_WEIGHTS.get(comp, 0) for comp in competencies if comp)
        return (total / 60) * 100 if total > 0 else 0
    
    def calculate_numerical_score(self):
        """Calculate raw numerical score (0-60)"""
        competencies = [self.foresight, self.judgement, self.oral_expression,
                       self.relations, self.punctuality, self.attendance,
                       self.industry, self.output_work, self.quality_work, self.honesty]
        return sum(self.GRADE_WEIGHTS.get(comp, 0) for comp in competencies if comp)
    
    def get_grade_description(self, grade):
        """Get description for a grade letter"""
        descriptions = {
            'A': 'Outstanding - Exceptionally high performance',
            'B': 'Very Good - Consistently exceeds expectations',
            'C': 'Good - Meets all requirements effectively',
            'D': 'Fair - Adequate but needs improvement',
            'E': 'Poor - Below acceptable standards',
            'F': 'Very Poor - Unacceptable performance'
        }
        return descriptions.get(grade, '')
    
    def get_overall_rating(self):
        """Get overall rating based on percentage score"""
        score = self.calculate_total_score()
        if score >= 90:
            return 'Outstanding'
        elif score >= 75:
            return 'Very Good'
        elif score >= 60:
            return 'Good'
        elif score >= 45:
            return 'Average'
        else:
            return 'Poor'
    
    @property
    def is_complete(self):
        """Check if assessment has all required grades"""
        required_fields = [self.foresight, self.judgement, self.oral_expression,
                          self.relations, self.punctuality, self.attendance,
                          self.industry, self.output_work]
        return all(required_fields)
    
    @property
    def has_countersignature(self):
        """Check if countersigning officer has signed"""
        return self.countersigning_officer_signature is not None
    
    @property
    def assessment_summary(self):
        """Return a summary of the assessment"""
        return {
            'total_score': self.calculate_total_score(),
            'numerical_score': self.calculate_numerical_score(),
            'rating': self.get_overall_rating(),
            'is_complete': self.is_complete,
            'has_countersignature': self.has_countersignature,
            'assessment_type': self.assessment_type
        }
    
    def to_dict(self):
        """Convert assessment to dictionary for API responses"""
        return {
            'id': self.id,
            'report_id': self.report_id,
            'scores': {
                'foresight': self.foresight,
                'judgement': self.judgement,
                'oral_expression': self.oral_expression,
                'relations': self.relations,
                'punctuality': self.punctuality,
                'attendance': self.attendance,
                'industry': self.industry,
                'output_work': self.output_work,
                'quality_work': self.quality_work,
                'honesty': self.honesty
            },
            'total_score': self.calculate_total_score(),
            'numerical_score': self.calculate_numerical_score(),
            'rating': self.get_overall_rating(),
            'general_remarks': self.general_remarks,
            'promotability_rating': self.promotability_rating,
            'assessment_type': self.assessment_type,
            'reviewer_id': self.reviewer_id,
            'review_date': self.review_date.isoformat() if self.review_date else None
        }
    
    def __repr__(self):
        return f'<Assessment Report {self.report_id} - {self.assessment_type}>'