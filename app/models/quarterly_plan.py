from app.extensions import db
from datetime import datetime
from enum import Enum

class PlanStatus:
    DRAFT = 'DRAFT'
    SUBMITTED = 'SUBMITTED'
    APPROVED = 'APPROVED'
    MODIFIED = 'MODIFIED'
    REJECTED = 'REJECTED'
    PENDING_CS_APPROVAL = 'PENDING_CS_APPROVAL'

class ReviewStatus:
    PENDING = 'PENDING'
    SUBMITTED = 'SUBMITTED'
    REVIEWED = 'REVIEWED'
    COMPLETED = 'COMPLETED'
    PENDING_CS_REVIEW = 'PENDING_CS_REVIEW'

class QuarterlyGoal(db.Model):
    __tablename__ = 'quarterly_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    planning_year = db.Column(db.Integer, nullable=False)
    quarter = db.Column(db.Integer, nullable=False)
    goal_description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.Integer, default=3)
    success_criteria = db.Column(db.Text)
    
    # Goal approval workflow
    plan_status = db.Column(db.String(50), default='DRAFT')
    plan_submitted_at = db.Column(db.DateTime)
    plan_approved_at = db.Column(db.DateTime)
    plan_approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    plan_modifications = db.Column(db.Text)
    
    # Countersigning Officer approval for GOALS
    cs_approved = db.Column(db.Boolean, default=False)
    cs_approved_at = db.Column(db.DateTime)
    cs_approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    cs_comments = db.Column(db.Text)
    
    # Quarterly review
    achievements = db.Column(db.Text)
    challenges = db.Column(db.Text)
    reasons_for_failure = db.Column(db.Text)
    recovery_plan = db.Column(db.Text)
    review_status = db.Column(db.String(50), default='PENDING')
    review_submitted_at = db.Column(db.DateTime)
    review_completed_at = db.Column(db.DateTime)
    review_completed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reporting_officer_comments = db.Column(db.Text)
    further_directives = db.Column(db.Text)
    quarter_2_adjustments = db.Column(db.Text)
    
    # Countersigning Officer review approval for QUARTERLY REVIEWS
    cs_review_approved = db.Column(db.Boolean, default=False)
    cs_review_approved_at = db.Column(db.DateTime)
    cs_review_approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    cs_review_comments = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='quarterly_goals')
    plan_approver = db.relationship('User', foreign_keys=[plan_approved_by], backref='approved_goals')
    cs_approver = db.relationship('User', foreign_keys=[cs_approved_by], backref='cs_approved_goals')
    cs_review_approver = db.relationship('User', foreign_keys=[cs_review_approved_by], backref='cs_reviewed_goals')
    review_completer = db.relationship('User', foreign_keys=[review_completed_by], backref='completed_reviews')
    
    def __repr__(self):
        return f'<QuarterlyGoal {self.planning_year} Q{self.quarter}>'

class YearlyAppraisal(db.Model):
    __tablename__ = 'yearly_appraisals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    appraisal_year = db.Column(db.Integer, nullable=False)
    
    # Officer's self-assessment (Section B from officer)
    section_b_work_output = db.Column(db.Float, default=0)
    section_b_innovation = db.Column(db.Float, default=0)
    section_b_leadership = db.Column(db.Float, default=0)
    section_b_teamwork = db.Column(db.Float, default=0)
    section_b_communication = db.Column(db.Float, default=0)
    section_b_ethics = db.Column(db.Float, default=0)
    section_b_total = db.Column(db.Float, default=0)
    
    # End of year report from officer
    annual_report = db.Column(db.Text)
    reasons_for_failure = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime)
    
    # Section A - Automatic grades from external systems
    training_attendance_score = db.Column(db.Integer, default=0)  # from JOOPSA
    clock_in_score = db.Column(db.Integer, default=0)  # from HRM
    peer_review_score = db.Column(db.Integer, default=0)  # 360 review
    
    # Section B - Reporting Officer's assessment (1-5 scale)
    diligently_executed = db.Column(db.Integer, default=3)
    delivered_timelines = db.Column(db.Integer, default=3)
    punctuality_effectiveness = db.Column(db.Integer, default=3)
    decency_presentability = db.Column(db.Integer, default=3)
    productivity = db.Column(db.Integer, default=3)
    communication_skills = db.Column(db.Integer, default=3)
    team_collaboration = db.Column(db.Integer, default=3)
    independent_work = db.Column(db.Integer, default=3)
    openness_to_learning = db.Column(db.Integer, default=3)
    proactivity_initiative = db.Column(db.Integer, default=3)
    
    # Reporting Officer's comments
    reporting_officer_comments = db.Column(db.Text)
    reporting_officer_sent_at = db.Column(db.DateTime)
    
    # Officer's response
    officer_agrees = db.Column(db.Boolean, default=None)
    officer_comments = db.Column(db.Text)
    officer_disagreement_reason = db.Column(db.Text)
    officer_response_at = db.Column(db.DateTime)
    
    # Permanent Secretary / Countersigning Officer review
    countersigning_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    ps_review_completed = db.Column(db.Boolean, default=False)
    ps_review_date = db.Column(db.DateTime)
    ps_comments = db.Column(db.Text)
    
    # Total score and rating
    total_score = db.Column(db.Float, default=0)
    rating = db.Column(db.String(50), default='Not Rated')
    
    # Final status
    status = db.Column(db.String(50), default='DRAFT')  # DRAFT, SUBMITTED, OFFICER_RESPONSE, RO_REVIEW, PS_REVIEW, FINALIZED
    finalized_at = db.Column(db.DateTime)
    
    # Workflow assignment
    reporting_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='yearly_appraisals')
    reporting_officer = db.relationship('User', foreign_keys=[reporting_officer_id], backref='ro_appraisals')
    countersigning_officer = db.relationship('User', foreign_keys=[countersigning_officer_id], backref='cs_appraisals')
    
    def calculate_section_b_total(self):
        """Calculate total for section B from RO ratings (max 40)"""
        # Convert 1-5 scale to 0-4 (each point = 1, max 10*4 = 40)
        scores = [
            (self.diligently_executed or 3) - 1,
            (self.delivered_timelines or 3) - 1,
            (self.punctuality_effectiveness or 3) - 1,
            (self.decency_presentability or 3) - 1,
            (self.productivity or 3) - 1,
            (self.communication_skills or 3) - 1,
            (self.team_collaboration or 3) - 1,
            (self.independent_work or 3) - 1,
            (self.openness_to_learning or 3) - 1,
            (self.proactivity_initiative or 3) - 1
        ]
        self.section_b_total = sum(scores)
        return self.section_b_total
    
    def __repr__(self):
        return f'<YearlyAppraisal {self.appraisal_year}>'