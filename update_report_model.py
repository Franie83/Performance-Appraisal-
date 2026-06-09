from app.extensions import db 
from datetime import datetime 
import inspect 
 
# Read current model file 
with open('app/models/performance_report.py', 'r') as f: 
    content = f.read() 
 
# Check if workflow fields already exist 
if 'target_reporting_officer_id' not in content: 
    # Add workflow fields before the last ')' or at the end of class 
    new_fields = ''' 
    # Workflow fields 
    target_reporting_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) 
    target_countersigning_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) 
    reporting_approved_at = db.Column(db.DateTime, nullable=True) 
    countersigning_approved_at = db.Column(db.DateTime, nullable=True) 
    reporting_approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) 
    countersigning_approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) 
    reporting_comments = db.Column(db.Text, nullable=True) 
    countersigning_comments = db.Column(db.Text, nullable=True) 
    final_status = db.Column(db.String(50), default='PENDING_REPORTING') 
    rejection_reason = db.Column(db.Text, nullable=True) 
 
    # Relationships 
    target_reporting_officer = db.relationship('User', foreign_keys=[target_reporting_officer_id], backref='assigned_reports') 
    target_countersigning_officer = db.relationship('User', foreign_keys=[target_countersigning_officer_id], backref='assigned_countersign_reports') 
    reporting_approver = db.relationship('User', foreign_keys=[reporting_approved_by]) 
    countersigning_approver = db.relationship('User', foreign_keys=[countersigning_approved_by]) 
''' 
 
    # Insert before the last line of the class 
    lines = content.split('\n') 
    # Find where to insert (before the last '    def' or before the class end) 
    insert_pos = len(lines) - 1 
    for i in range(len(lines)-1, -1, -1): 
        if lines[i].strip().startswith('def '): 
            insert_pos = i 
            break 
 
    new_lines = lines[:insert_pos] + new_fields.split('\n') + lines[insert_pos:] 
    with open('app/models/performance_report.py', 'w') as f: 
        f.write('\n'.join(new_lines)) 
    print('PerformanceReport model updated with workflow fields') 
else: 
    print('Workflow fields already exist') 
