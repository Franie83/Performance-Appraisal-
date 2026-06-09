# app/utils/audit_logger.py
from app.extensions import db
from app.models.audit_log import AuditLog
from flask import request
import json
from datetime import datetime

class AuditLogger:
    @staticmethod
    def log(user, action, entity_type, entity_id=None, entity_name=None, 
            old_value=None, new_value=None, changes=None):
        """Create an audit log entry"""
        try:
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
    
    @staticmethod
    def log_user_create(user, created_by, new_user_data):
        """Log user creation"""
        AuditLogger.log(
            user=created_by,
            action='CREATE',
            entity_type='USER',
            entity_id=new_user_data.get('id'),
            entity_name=new_user_data.get('username'),
            new_value=json.dumps(new_user_data, default=str)
        )
    
    @staticmethod
    def log_user_update(user, updated_by, user_id, username, changes):
        """Log user update"""
        AuditLogger.log(
            user=updated_by,
            action='UPDATE',
            entity_type='USER',
            entity_id=user_id,
            entity_name=username,
            changes=json.dumps(changes, default=str)
        )
    
    @staticmethod
    def log_user_delete(user, deleted_by, user_id, username, user_data):
        """Log user deletion"""
        AuditLogger.log(
            user=deleted_by,
            action='DELETE',
            entity_type='USER',
            entity_id=user_id,
            entity_name=username,
            old_value=json.dumps(user_data, default=str)
        )
    
    @staticmethod
    def log_profile_update(user, updated_by, user_id, username, changes):
        """Log profile update"""
        AuditLogger.log(
            user=updated_by,
            action='UPDATE',
            entity_type='PROFILE',
            entity_id=user_id,
            entity_name=username,
            changes=json.dumps(changes, default=str)
        )