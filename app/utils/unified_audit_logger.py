# app/utils/unified_audit_logger.py
from app.extensions import db
from app.models.audit_log import AuditLog
from flask import request
import json
from datetime import datetime

class UnifiedAuditLogger:
    """Unified audit logger for both Gen 79A and Quarterly systems"""
    
    @staticmethod
    def log(user, action, entity_type, entity_id=None, entity_name=None, 
            old_value=None, new_value=None, changes=None, module=None):
        """Create an audit log entry"""
        try:
            # Determine module if not specified
            if not module:
                if 'quarterly' in str(request.url_rule):
                    module = 'QUARTERLY'
                elif 'reports' in str(request.url_rule):
                    module = 'GEN79A'
                else:
                    module = 'SYSTEM'
            
            audit = AuditLog(
                user_id=user.id,
                username=user.username,
                user_role=user.role,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                entity_name=entity_name,
                old_value=old_value,
                new_value=new_value,
                changes=changes,
                ip_address=request.remote_addr if request else None,
                user_agent=request.headers.get('User-Agent', '')[:300] if request else None,
                created_at=datetime.utcnow()
            )
            db.session.add(audit)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Failed to log audit: {e}")
    
    # ============ GEN 79A (First Leg) Methods ============
    
    @staticmethod
    def log_gen79a_create(user, report_id, officer_name, report_data):
        """Log Gen 79A report creation"""
        UnifiedAuditLogger.log(
            user=user,
            action='CREATE',
            entity_type='GEN79A_REPORT',
            entity_id=report_id,
            entity_name=f"Report for {officer_name}",
            new_value=json.dumps(report_data, default=str),
            module='GEN79A'
        )
    
    @staticmethod
    def log_gen79a_submit(user, report_id, officer_name):
        """Log Gen 79A report submission"""
        UnifiedAuditLogger.log(
            user=user,
            action='SUBMIT',
            entity_type='GEN79A_REPORT',
            entity_id=report_id,
            entity_name=f"Report for {officer_name}",
            new_value="Submitted for approval",
            module='GEN79A'
        )
    
    @staticmethod
    def log_gen79a_assess(user, report_id, officer_name, assessment, comments):
        """Log Gen 79A RO assessment"""
        UnifiedAuditLogger.log(
            user=user,
            action='ASSESS',
            entity_type='GEN79A_REPORT',
            entity_id=report_id,
            entity_name=f"Report for {officer_name}",
            new_value=f"Assessment: {assessment}, Comments: {comments[:100]}",
            module='GEN79A'
        )
    
    @staticmethod
    def log_gen79a_countersign(user, report_id, officer_name, action, comments):
        """Log Gen 79A countersigning action"""
        UnifiedAuditLogger.log(
            user=user,
            action='COUNTERSIGN',
            entity_type='GEN79A_REPORT',
            entity_id=report_id,
            entity_name=f"Report for {officer_name}",
            new_value=f"Action: {action}, Comments: {comments[:100] if comments else 'None'}",
            module='GEN79A'
        )
    
    @staticmethod
    def log_gen79a_update(user, report_id, officer_name, changes):
        """Log Gen 79A report update"""
        UnifiedAuditLogger.log(
            user=user,
            action='UPDATE',
            entity_type='GEN79A_REPORT',
            entity_id=report_id,
            entity_name=f"Report for {officer_name}",
            changes=json.dumps(changes, default=str),
            module='GEN79A'
        )
    
    @staticmethod
    def log_gen79a_delete(user, report_id, officer_name, report_data):
        """Log Gen 79A report deletion"""
        UnifiedAuditLogger.log(
            user=user,
            action='DELETE',
            entity_type='GEN79A_REPORT',
            entity_id=report_id,
            entity_name=f"Report for {officer_name}",
            old_value=json.dumps(report_data, default=str),
            module='GEN79A'
        )
    
    # ============ QUARTERLY (Second Leg) Methods ============
    
    @staticmethod
    def log_quarterly_goal_create(user, goal_id, officer_name, goal_data):
        """Log quarterly goal creation"""
        UnifiedAuditLogger.log(
            user=user,
            action='CREATE',
            entity_type='QUARTERLY_GOAL',
            entity_id=goal_id,
            entity_name=f"Goal for {officer_name}",
            new_value=json.dumps(goal_data, default=str),
            module='QUARTERLY'
        )
    
    @staticmethod
    def log_quarterly_goal_submit(user, goal_id, officer_name):
        """Log quarterly goal submission"""
        UnifiedAuditLogger.log(
            user=user,
            action='SUBMIT',
            entity_type='QUARTERLY_GOAL',
            entity_id=goal_id,
            entity_name=f"Goal for {officer_name}",
            new_value="Submitted for approval",
            module='QUARTERLY'
        )
    
    @staticmethod
    def log_quarterly_goal_approve(user, goal_id, officer_name, approval_level):
        """Log quarterly goal approval (RO or CS)"""
        UnifiedAuditLogger.log(
            user=user,
            action='APPROVE',
            entity_type='QUARTERLY_GOAL',
            entity_id=goal_id,
            entity_name=f"Goal for {officer_name}",
            new_value=f"Approved by {approval_level}",
            module='QUARTERLY'
        )
    
    @staticmethod
    def log_quarterly_review_submit(user, goal_id, officer_name, quarter):
        """Log quarterly review submission"""
        UnifiedAuditLogger.log(
            user=user,
            action='SUBMIT',
            entity_type='QUARTERLY_REVIEW',
            entity_id=goal_id,
            entity_name=f"Q{quarter} review for {officer_name}",
            new_value="Submitted for review",
            module='QUARTERLY'
        )
    
    @staticmethod
    def log_quarterly_review_assess(user, goal_id, officer_name, quarter, assessment):
        """Log quarterly review assessment by RO"""
        UnifiedAuditLogger.log(
            user=user,
            action='ASSESS',
            entity_type='QUARTERLY_REVIEW',
            entity_id=goal_id,
            entity_name=f"Q{quarter} review for {officer_name}",
            new_value=f"Assessment: {assessment}",
            module='QUARTERLY'
        )
    
    @staticmethod
    def log_yearly_appraisal_create(user, appraisal_id, officer_name, year):
        """Log yearly appraisal creation"""
        UnifiedAuditLogger.log(
            user=user,
            action='CREATE',
            entity_type='YEARLY_APPRAISAL',
            entity_id=appraisal_id,
            entity_name=f"Appraisal for {officer_name} - {year}",
            module='QUARTERLY'
        )
    
    @staticmethod
    def log_yearly_appraisal_submit(user, appraisal_id, officer_name, year):
        """Log yearly appraisal submission"""
        UnifiedAuditLogger.log(
            user=user,
            action='SUBMIT',
            entity_type='YEARLY_APPRAISAL',
            entity_id=appraisal_id,
            entity_name=f"Appraisal for {officer_name} - {year}",
            new_value="Submitted for review",
            module='QUARTERLY'
        )
    
    @staticmethod
    def log_yearly_appraisal_finalize(user, appraisal_id, officer_name, year):
        """Log yearly appraisal finalization by CS"""
        UnifiedAuditLogger.log(
            user=user,
            action='FINALIZE',
            entity_type='YEARLY_APPRAISAL',
            entity_id=appraisal_id,
            entity_name=f"Appraisal for {officer_name} - {year}",
            new_value="Finalized by Countersigning Officer",
            module='QUARTERLY'
        )