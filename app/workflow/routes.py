from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.performance_report import PerformanceReport
from app.models.officer import Officer
from app.models.user import User
from app.workflow import workflow_bp
from datetime import datetime

@workflow_bp.route('/assign-supervisors')
@login_required
def assign_supervisors():
    if not current_user.has_role('ADMIN'):
        flash('Access denied', 'danger')
        return redirect(url_for('reports.dashboard'))
    
    officers = Officer.query.all()
    users = User.query.filter(User.role.in_(['REPORTING_OFFICER', 'COUNTERSIGNING_OFFICER'])).all()
    return render_template('workflow/assign_supervisors.html', officers=officers, users=users)

@login_required
def assign_reporting_officer(officer_id):
    if not current_user.has_role('ADMIN'):
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    officer = Officer.query.get_or_404(officer_id)
    reporting_id = request.form.get('reporting_officer_id')
    
    if reporting_id:
        officer.reporting_officer_id = int(reporting_id)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Reporting officer assigned'})
    
    return jsonify({'success': False, 'message': 'Invalid selection'})
