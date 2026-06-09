# app/models/audit_log.py
from app.extensions import db
from datetime import datetime

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    user_role = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # CREATE, UPDATE, DELETE, SUBMIT, APPROVE, ASSESS, COUNTERSIGN, FINALIZE, EXPORT, BULK_APPROVE, CLEAR_DATA, LOGIN, LOGOUT
    entity_type = db.Column(db.String(50), nullable=False)  # USER, PROFILE, GOAL, REVIEW, APPRAISAL, GEN79A_REPORT, QUARTERLY_GOAL, QUARTERLY_REVIEW, YEARLY_APPRAISAL, SYSTEM
    entity_id = db.Column(db.Integer, nullable=True)
    entity_name = db.Column(db.String(200), nullable=True)
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    changes = db.Column(db.Text, nullable=True)  # JSON string of changes
    module = db.Column(db.String(50), nullable=True)  # GEN79A, QUARTERLY, SYSTEM
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', foreign_keys=[user_id], backref='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.action} {self.entity_type} by {self.username}>'
    
    def to_dict(self):
        """Convert audit log to dictionary for display"""
        return {
            'id': self.id,
            'username': self.username,
            'user_role': self.user_role,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_name': self.entity_name,
            'changes': self.changes,
            'module': self.module,
            'ip_address': self.ip_address,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
    
    @staticmethod
    def get_action_badge_class(action):
        """Return badge class for action type"""
        action_classes = {
            'CREATE': 'bg-success',
            'UPDATE': 'bg-warning text-dark',
            'DELETE': 'bg-danger',
            'SUBMIT': 'bg-info',
            'APPROVE': 'bg-success',
            'ASSESS': 'bg-primary',
            'COUNTERSIGN': 'bg-secondary',
            'FINALIZE': 'bg-success',
            'EXPORT': 'bg-secondary',
            'BULK_APPROVE': 'bg-warning text-dark',
            'CLEAR_DATA': 'bg-danger',
            'LOGIN': 'bg-info',
            'LOGOUT': 'bg-secondary'
        }
        return action_classes.get(action, 'bg-secondary')
    
    @staticmethod
    def get_entity_badge_class(entity_type):
        """Return badge class for entity type"""
        entity_classes = {
            'USER': 'bg-dark',
            'PROFILE': 'bg-dark',
            'GEN79A_REPORT': 'bg-primary',
            'QUARTERLY_GOAL': 'bg-success',
            'QUARTERLY_REVIEW': 'bg-info',
            'YEARLY_APPRAISAL': 'bg-warning text-dark',
            'SYSTEM': 'bg-danger'
        }
        return entity_classes.get(entity_type, 'bg-secondary')
    
    @staticmethod
    def get_module_badge_class(module):
        """Return badge class for module"""
        module_classes = {
            'GEN79A': 'bg-primary',
            'QUARTERLY': 'bg-success',
            'SYSTEM': 'bg-danger'
        }
        return module_classes.get(module, 'bg-secondary')