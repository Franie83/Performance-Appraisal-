from app.extensions import db
from datetime import datetime, date
import secrets

class PerformanceReport(db.Model):
    __tablename__ = 'performance_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_year = db.Column(db.Integer, nullable=False)
    period_from = db.Column(db.Date, nullable=False)
    period_to = db.Column(db.Date, nullable=False)
    
    # Section 2: Personal Particulars
    date_of_birth = db.Column(db.Date)
    date_first_appointment = db.Column(db.Date)
    post_appointed = db.Column(db.String(200))
    present_post = db.Column(db.String(200))
    present_post_date = db.Column(db.Date)
    salary_grade = db.Column(db.String(50))
    incremental_date = db.Column(db.Date)
    educational_qualifications = db.Column(db.Text)
    date_appointment_confirmed = db.Column(db.Date)
    
    # Section 3: Leave Information
    sick_leave_days = db.Column(db.Integer, default=0)
    sick_leave_details = db.Column(db.Text)
    ncl_days = db.Column(db.Integer, default=0)
    ncl_details = db.Column(db.Text)
    annual_leave_days = db.Column(db.Integer, default=0)
    casual_leave_days = db.Column(db.Integer, default=0)
    
    # Section 4: Target Setting & Achievements
    division_targets = db.Column(db.Text)
    appraiser_targets = db.Column(db.Text)
    estimated_salary_cost = db.Column(db.Numeric(15, 2))
    estimated_overhead_cost = db.Column(db.Numeric(15, 2))
    estimated_capital_cost = db.Column(db.Numeric(15, 2))
    agreed_completion_time = db.Column(db.String(200))
    quantity_conform_standard = db.Column(db.Boolean, default=False)
    quality_conform_standard = db.Column(db.Boolean, default=False)
    
    # Section 5: Job Description
    main_duties = db.Column(db.Text)
    joint_discussion_with_supervisor = db.Column(db.Boolean, default=False)
    properly_equipped = db.Column(db.Boolean, default=True)
    constraints_difficulties = db.Column(db.Text)
    
    # Section 7: Difficulties and Solutions
    difficulties_encountered = db.Column(db.Text)
    supervisor_assistance_methods = db.Column(db.Text)
    periodic_review_frequency = db.Column(db.String(50))
    performance_measured_up = db.Column(db.Boolean, default=False)
    solution_admonition = db.Column(db.Text)
    final_evaluation_done = db.Column(db.Boolean, default=False)
    
    # Ad hoc duties
    ad_hoc_duties = db.Column(db.Text)
    ad_hoc_duties_affected = db.Column(db.Boolean, default=False)
    ad_hoc_brought_to_supervisor = db.Column(db.Boolean, default=False)
    
    # Service periods
    schedule_duty_from = db.Column(db.Date)
    schedule_duty_to = db.Column(db.Date)
    
    # Supervisors during period
    supervisor1_name = db.Column(db.String(200))
    supervisor1_from = db.Column(db.Date)
    supervisor1_to = db.Column(db.Date)
    supervisor2_name = db.Column(db.String(200))
    supervisor2_from = db.Column(db.Date)
    supervisor2_to = db.Column(db.Date)
    supervisor3_name = db.Column(db.String(200))
    supervisor3_from = db.Column(db.Date)
    supervisor3_to = db.Column(db.Date)
    
    # Section 6: Performance Assessment (from Reporting Officer)
    # Fixed relationship with overlaps parameter to silence warning
    assessment = db.relationship('Assessment', backref='performance_report', 
                                 uselist=False, cascade='all, delete-orphan',
                                 overlaps='assessments,report')
    
    # Section 8: Training and Promotability
    training_recommended = db.Column(db.Text)
    promotability_rating = db.Column(db.String(20))
    promotion_reason = db.Column(db.Text)
    accelerated_promotion_recommendation = db.Column(db.Text)
    
    # Section 11: Officer's Declaration
    officer_has_seen_report = db.Column(db.Boolean, default=False)
    officer_comments = db.Column(db.Text)
    officer_declaration_date = db.Column(db.Date)
    
    # Section 12: Reporting Officer's Declaration
    reporting_officer_signature = db.Column(db.Boolean, default=False)
    reporting_officer_name = db.Column(db.String(200))
    reporting_officer_position = db.Column(db.String(200))
    reporting_officer_grade = db.Column(db.String(50))
    reporting_officer_date = db.Column(db.Date)
    
    # Section 13: Countersigning Officer's Report
    countersigning_agrees = db.Column(db.Boolean, default=False)
    countersigning_disagreement_notes = db.Column(db.Text)
    years_served_under = db.Column(db.String(50))
    countersigning_adverse_comments = db.Column(db.Text)
    countersigning_officer_signature = db.Column(db.Boolean, default=False)
    countersigning_officer_name = db.Column(db.String(200))
    countersigning_officer_position = db.Column(db.String(200))
    countersigning_officer_grade = db.Column(db.String(50))
    countersigning_officer_date = db.Column(db.Date)
    
    # Workflow fields
    status = db.Column(db.String(50), default='DRAFT')
    final_status = db.Column(db.String(50), default='PENDING_REPORTING')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = db.Column(db.DateTime)
    
    # Verification
    verification_code = db.Column(db.String(100), unique=True, nullable=True)
    
    # Workflow assignment
    target_reporting_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    target_countersigning_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reporting_approved_at = db.Column(db.DateTime, nullable=True)
    reporting_approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reporting_comments = db.Column(db.Text, nullable=True)
    countersigning_approved_at = db.Column(db.DateTime, nullable=True)
    countersigning_approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    countersigning_comments = db.Column(db.Text, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # Relationships
    staff = db.relationship('User', foreign_keys=[user_id], backref='reports')
    target_reporting_officer = db.relationship('User', foreign_keys=[target_reporting_officer_id])
    target_countersigning_officer = db.relationship('User', foreign_keys=[target_countersigning_officer_id])
    
    def __repr__(self):
        return f'<PerformanceReport {self.report_year} - {self.status}>'