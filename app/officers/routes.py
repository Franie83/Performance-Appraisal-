from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.officer import Officer
from app.models.user import User
from app.officers import officers_bp
import logging

logger = logging.getLogger(__name__)


@officers_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Allow all officer-related roles and admin
    allowed_roles = ['OFFICER', 'REPORTING_OFFICER', 'COUNTERSIGNING_OFFICER', 'HR', 'ADMIN']
    if current_user.role not in allowed_roles:
        flash('Only officers can access this page', 'danger')
        return redirect(url_for('reports.dashboard'))
    
    # Get or create officer profile
    officer = Officer.query.filter_by(user_id=current_user.id).first()
    
    # If no officer profile exists, create one automatically
    if not officer:
        officer = Officer(
            user_id=current_user.id,
            surname=current_user.surname or current_user.username,
            first_name=current_user.first_name or '',
            staff_no=current_user.staff_no or f'STAFF{current_user.id:03d}',
            title='Mr',
            ministry=current_user.ministry or 'Ministry not set',
            department=current_user.department or 'Department not set'
        )
        db.session.add(officer)
        db.session.commit()
        flash('Officer profile created automatically. Please complete your details.', 'info')
    
    if request.method == 'POST':
        try:
            new_staff_no = request.form.get('staff_no')
            if new_staff_no and officer.staff_no != new_staff_no:
                existing_officer = Officer.query.filter(
                    Officer.staff_no == new_staff_no,
                    Officer.id != officer.id
                ).first()
                if existing_officer:
                    flash(f'Staff number {new_staff_no} is already assigned to another officer', 'danger')
                    return redirect(url_for('officers.profile'))
            
            officer.staff_no = new_staff_no
            officer.surname = request.form.get('surname')
            officer.first_name = request.form.get('first_name')
            officer.other_names = request.form.get('other_names')
            officer.title = request.form.get('title')
            officer.ministry = request.form.get('ministry')
            officer.department = request.form.get('department')
            officer.division = request.form.get('division')
            officer.branch = request.form.get('branch')
            officer.section = request.form.get('section')
            
            # Also update the corresponding User fields for consistency
            if officer.surname:
                current_user.surname = officer.surname
            if officer.first_name:
                current_user.first_name = officer.first_name
            if officer.staff_no:
                current_user.staff_no = officer.staff_no
            if officer.ministry:
                current_user.ministry = officer.ministry
            if officer.department:
                current_user.department = officer.department
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating profile: {str(e)}")
            flash(f'Error updating profile: {str(e)}', 'danger')
        
        return redirect(url_for('officers.profile'))
    
    return render_template('officers/profile.html', officer=officer)


@officers_bp.route('/check-staff-no', methods=['GET'])
@login_required
def check_staff_no():
    """Check if staff number is available for AJAX validation"""
    staff_no = request.args.get('staff_no')
    officer_id = request.args.get('officer_id', type=int)
    
    if not staff_no:
        return jsonify({'available': False, 'message': 'No staff number provided'})
    
    query = Officer.query.filter(Officer.staff_no == staff_no)
    if officer_id:
        query = query.filter(Officer.id != officer_id)
    
    existing = query.first()
    
    if existing:
        return jsonify({'available': False, 'message': f'Staff number {staff_no} is already taken'})
    else:
        return jsonify({'available': True, 'message': 'Staff number is available'})