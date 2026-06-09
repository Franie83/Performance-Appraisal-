import os 
 
# Create workflow directory 
os.makedirs('app/workflow', exist_ok=True) 
 
# Create __init__.py 
with open('app/workflow/__init__.py', 'w') as f: 
    f.write('from flask import Blueprint\n') 
    f.write('\n') 
    f.write('workflow_bp = Blueprint(\'workflow\', __name__)\n') 
    f.write('\n') 
    f.write('from app.workflow import routes\n') 
 
# Create routes.py 
with open('app/workflow/routes.py', 'w') as f: 
    f.write('from flask import render_template, redirect, url_for, flash, request, jsonify\n') 
    f.write('from flask_login import login_required, current_user\n') 
    f.write('from app.extensions import db\n') 
    f.write('from app.models.performance_report import PerformanceReport\n') 
    f.write('from app.models.officer import Officer\n') 
    f.write('from app.models.user import User\n') 
    f.write('from app.workflow import workflow_bp\n') 
    f.write('from datetime import datetime\n') 
    f.write('\n') 
    f.write('@workflow_bp.route(\'/assign-supervisors\')\n') 
    f.write('@login_required\n') 
    f.write('def assign_supervisors():\n') 
    f.write('    if not current_user.has_role(\'ADMIN\'):\n') 
    f.write('        flash(\'Access denied\', \'danger\')\n') 
    f.write('        return redirect(url_for(\'reports.dashboard\'))\n') 
    f.write('    \n') 
    f.write('    officers = Officer.query.all()\n') 
    f.write('    users = User.query.filter(User.role.in_([\'REPORTING_OFFICER\', \'COUNTERSIGNING_OFFICER\'])).all()\n') 
    f.write('    return render_template(\'workflow/assign_supervisors.html\', officers=officers, users=users)\n') 
    f.write('\n') 
    f.write('@login_required\n') 
    f.write('def assign_reporting_officer(officer_id):\n') 
    f.write('    if not current_user.has_role(\'ADMIN\'):\n') 
    f.write('        return jsonify({\'success\': False, \'message\': \'Unauthorized\'})\n') 
    f.write('    \n') 
    f.write('    officer = Officer.query.get_or_404(officer_id)\n') 
    f.write('    reporting_id = request.form.get(\'reporting_officer_id\')\n') 
    f.write('    \n') 
    f.write('    if reporting_id:\n') 
    f.write('        officer.reporting_officer_id = int(reporting_id)\n') 
    f.write('        db.session.commit()\n') 
    f.write('        return jsonify({\'success\': True, \'message\': \'Reporting officer assigned\'})\n') 
    f.write('    \n') 
    f.write('    return jsonify({\'success\': False, \'message\': \'Invalid selection\'})\n') 
 
print('Workflow module created successfully!') 
