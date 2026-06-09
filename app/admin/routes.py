from flask import request, jsonify, render_template, redirect, url_for, flash, Response, session
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.officer import Officer
from app.models.performance_report import PerformanceReport
from app.models.assessment import Assessment
from app.admin import admin_bp
import logging
import csv
from io import StringIO
from datetime import datetime
from app.models.system_settings import SystemSetting
import os
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload   # ADDED for eager loading

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@admin_bp.route('/manage-users')
@login_required
def manage_users():
    """Display manage users page"""
    if not current_user.has_role('ADMIN'):
        flash('Access denied', 'danger')
        return redirect(url_for('reports.dashboard'))
    
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)


@admin_bp.route('/create-user-page')
@login_required
def create_user_page():
    """Standalone create user page"""
    if not current_user.has_role('ADMIN'):
        flash('Access denied', 'danger')
        return redirect(url_for('reports.dashboard'))
    
    return render_template('admin/admin_create_user.html')


@admin_bp.route('/edit-user-page/<int:user_id>')
@login_required
def edit_user_page(user_id):
    """Standalone edit user page"""
    if not current_user.has_role('ADMIN'):
        flash('Access denied', 'danger')
        return redirect(url_for('reports.dashboard'))
    
    user = User.query.get_or_404(user_id)
    return render_template('admin/admin_edit_user.html', user=user)


@admin_bp.route('/bulk-upload', methods=['GET'])
@login_required
def bulk_upload_page():
    """Display bulk upload page"""
    if not current_user.has_role('ADMIN'):
        flash('Access denied', 'danger')
        return redirect(url_for('reports.dashboard'))
    
    return render_template('admin/bulk_upload.html')


@admin_bp.route('/manage-officers')
@login_required
def manage_officers():
    """Display manage officers page - optionally filtered by user_id"""
    if not current_user.has_role('ADMIN'):
        flash('Access denied', 'danger')
        return redirect(url_for('reports.dashboard'))
    
    user_id = request.args.get('user_id', type=int)
    
    if user_id:
        officer = Officer.query.filter_by(user_id=user_id).first()
        user = User.query.get(user_id)
        if officer:
            officers = [officer]
            flash(f'Showing officer profile for: {user.full_name or user.username}', 'info')
        else:
            officers = []
            flash(f'No officer profile found for {user.full_name or user.username}', 'warning')
    else:
        officers = Officer.query.all()
    
    return render_template('admin/manage_officers.html', officers=officers, filter_user_id=user_id)


@admin_bp.route('/edit-officer-profile/<int:officer_id>', methods=['GET', 'POST'])
@login_required
def edit_officer_profile(officer_id):
    """Edit officer profile"""
    if not current_user.has_role('ADMIN'):
        flash('Access denied', 'danger')
        return redirect(url_for('reports.dashboard'))
    
    officer = Officer.query.get_or_404(officer_id)
    filter_user_id = request.args.get('user_id', type=int)
    
    if request.method == 'POST':
        officer.title = request.form.get('title')
        officer.staff_no = request.form.get('staff_no')
        officer.surname = request.form.get('surname')
        officer.first_name = request.form.get('first_name')
        officer.other_names = request.form.get('other_names')
        
        date_of_birth_str = request.form.get('date_of_birth')
        if date_of_birth_str:
            try:
                officer.date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
            except ValueError:
                officer.date_of_birth = None
        else:
            officer.date_of_birth = None
        
        date_first_appointment_str = request.form.get('date_first_appointment')
        if date_first_appointment_str:
            try:
                officer.date_first_appointment = datetime.strptime(date_first_appointment_str, '%Y-%m-%d').date()
            except ValueError:
                officer.date_first_appointment = None
        else:
            officer.date_first_appointment = None
        
        officer.post_appointed = request.form.get('post_appointed')
        officer.present_post = request.form.get('present_post')
        officer.salary_grade = request.form.get('salary_grade')
        officer.ministry = request.form.get('ministry')
        officer.department = request.form.get('department')
        officer.division = request.form.get('division')
        officer.branch = request.form.get('branch')
        officer.section = request.form.get('section')
        
        if officer.user:
            officer.user.surname = officer.surname
            officer.user.first_name = officer.first_name
            officer.user.staff_no = officer.staff_no
            officer.user.ministry = officer.ministry
            officer.user.department = officer.department
        
        db.session.commit()
        flash(f'Officer profile for {officer.full_name} updated successfully!', 'success')
        
        if filter_user_id:
            return redirect(url_for('admin.manage_officers', user_id=filter_user_id))
        else:
            return redirect(url_for('admin.manage_officers'))
    
    return render_template('admin/edit_officer_profile.html', officer=officer, filter_user_id=filter_user_id)


@admin_bp.route('/delete-officer/<int:officer_id>', methods=['DELETE'])
@login_required
def delete_officer(officer_id):
    """Delete an officer profile"""
    if not current_user.has_role('ADMIN'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    officer = Officer.query.get_or_404(officer_id)
    db.session.delete(officer)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Officer profile deleted successfully'})


@admin_bp.route('/manage-reports')
@login_required
def manage_reports():
    """Display manage reports page - optionally filtered by user_id"""
    if not current_user.has_role('ADMIN'):
        flash('Access denied', 'danger')
        return redirect(url_for('reports.dashboard'))
    
    user_id = request.args.get('user_id', type=int)
    
    # No joinedload – simply query reports
    query = PerformanceReport.query
    
    if user_id:
        query = query.filter(PerformanceReport.user_id == user_id)
        user = User.query.get(user_id)
        if user:
            flash(f'Showing reports for: {user.full_name or user.username}', 'info')
        reports = query.order_by(PerformanceReport.created_at.desc()).all()
    else:
        reports = query.order_by(PerformanceReport.created_at.desc()).all()
    
    # Get distinct years for filter dropdown
    available_years = db.session.query(PerformanceReport.report_year).distinct().order_by(PerformanceReport.report_year.desc()).all()
    available_years = [year[0] for year in available_years if year[0]]
    
    # Pre-load users for all reports to avoid N+1 (optional)
    user_ids = list(set(r.user_id for r in reports))
    users = {u.id: u for u in User.query.filter(User.id.in_(user_ids)).all()} if user_ids else {}
    
    return render_template('admin/manage_reports.html', 
                         reports=reports, 
                         filter_user_id=user_id,
                         available_years=available_years,
                         users=users)   # pass users dictionary

@admin_bp.route('/edit-report/<int:report_id>', methods=['GET', 'POST'])
@login_required
def edit_report(report_id):
    """Edit a performance report"""
    if not current_user.has_role('ADMIN'):
        flash('Access denied', 'danger')
        return redirect(url_for('reports.dashboard'))
    
    report = PerformanceReport.query.get_or_404(report_id)
    assessment = Assessment.query.filter_by(report_id=report_id).first()
    users = User.query.all()
    officers = Officer.query.all()
    filter_user_id = request.args.get('user_id', type=int)
    
    # Auto-assign Reporting Officer and Countersigning Officer
    staff_user = User.query.get(report.user_id)
    
    if staff_user and not report.target_reporting_officer_id:
        reporting_officer = User.query.filter(
            User.role == 'REPORTING_OFFICER',
            User.ministry == staff_user.ministry,
            User.department == staff_user.department,
            User.is_active == True
        ).first()
        
        if reporting_officer:
            report.target_reporting_officer_id = reporting_officer.id
    
    if staff_user and not report.target_countersigning_officer_id:
        countersigning_officer = User.query.filter(
            User.role == 'COUNTERSIGNING_OFFICER',
            User.ministry == staff_user.ministry,
            User.is_active == True
        ).first()
        
        if countersigning_officer:
            report.target_countersigning_officer_id = countersigning_officer.id
    
    db.session.commit()
    
    if request.method == 'POST':
        report.report_year = int(request.form.get('report_year'))
        report.period_from = datetime.strptime(request.form.get('period_from'), '%Y-%m-%d')
        report.period_to = datetime.strptime(request.form.get('period_to'), '%Y-%m-%d')
        report.division_targets = request.form.get('division_targets')
        report.appraiser_targets = request.form.get('appraiser_targets')
        report.main_duties = request.form.get('main_duties')
        report.constraints_difficulties = request.form.get('constraints_difficulties')
        report.status = request.form.get('status')
        report.final_status = request.form.get('final_status')
        
        if request.form.get('target_reporting_officer_id'):
            report.target_reporting_officer_id = int(request.form.get('target_reporting_officer_id'))
        if request.form.get('target_countersigning_officer_id'):
            report.target_countersigning_officer_id = int(request.form.get('target_countersigning_officer_id'))
        
        if request.form.get('reporting_approved_at'):
            try:
                report.reporting_approved_at = datetime.strptime(request.form.get('reporting_approved_at'), '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass
        if request.form.get('countersigning_approved_at'):
            try:
                report.countersigning_approved_at = datetime.strptime(request.form.get('countersigning_approved_at'), '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass
        
        report.reporting_comments = request.form.get('reporting_comments')
        report.countersigning_comments = request.form.get('countersigning_comments')
        report.rejection_reason = request.form.get('rejection_reason')
        
        if request.form.get('has_assessment') == 'on':
            if not assessment:
                assessment = Assessment(report_id=report_id)
                db.session.add(assessment)
            
            assessment.foresight = request.form.get('foresight')
            assessment.judgement = request.form.get('judgement')
            assessment.oral_expression = request.form.get('oral_expression')
            assessment.relations = request.form.get('relations')
            assessment.punctuality = request.form.get('punctuality')
            assessment.attendance = request.form.get('attendance')
            assessment.industry = request.form.get('industry')
            assessment.output_work = request.form.get('output_work')
            assessment.quality_work = request.form.get('quality_work')
            assessment.honesty = request.form.get('honesty')
            assessment.general_remarks = request.form.get('general_remarks')
            assessment.training_recommended = request.form.get('training_recommended')
            assessment.promotability_rating = request.form.get('promotability_rating')
        elif assessment and request.form.get('has_assessment') != 'on':
            db.session.delete(assessment)
        
        db.session.commit()
        flash(f'Report #{report.id} updated successfully!', 'success')
        
        if filter_user_id:
            return redirect(url_for('admin.manage_reports', user_id=filter_user_id))
        else:
            return redirect(url_for('admin.manage_reports'))
    
    return render_template('admin/edit_report.html', report=report, assessment=assessment, users=users, officers=officers, filter_user_id=filter_user_id)


@admin_bp.route('/export-users', methods=['GET'])
@login_required
def export_users():
    """Export users to CSV"""
    try:
        if not current_user.has_role('ADMIN'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        users = User.query.all()
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['ID', 'Username', 'Email', 'Role', 'Department', 'Ministry', 'Staff No', 'Full Name', 'Status', 'Created At'])
        
        for user in users:
            writer.writerow([
                user.id, user.username, user.email, user.role,
                user.department or '', user.ministry or '',
                user.staff_no or '', user.full_name,
                'Active' if user.is_active else 'Inactive',
                user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else ''
            ])
        
        response = Response(output.getvalue(), mimetype='text/csv',
                          headers={'Content-Disposition': 'attachment; filename=users_export.csv'})
        return response
    except Exception as e:
        logger.error(f"Error exporting users: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@admin_bp.route('/seed-users', methods=['POST', 'GET'])
@login_required
def seed_users():
    """Seed test users into the database"""
    try:
        if not current_user.has_role('ADMIN'):
            return jsonify({'success': False, 'message': 'Unauthorized - Admin access required'}), 403

        test_users = [
            {'username': 'hr_officer', 'email': 'hr@example.com', 'password': 'Hr@123', 'role': 'HR', 'department': None, 'ministry': None},
            {'username': 'reporting_officer', 'email': 'reporting@example.com', 'password': 'Report@123', 'role': 'REPORTING_OFFICER', 'department': 'Digital Economy and Innovation', 'ministry': None},
            {'username': 'countersigning_officer', 'email': 'countersign@example.com', 'password': 'Countersign@123', 'role': 'COUNTERSIGNING_OFFICER', 'department': None, 'ministry': 'Ministry of Digital Economy'},
            {'username': 'john_doe', 'email': 'john@example.com', 'password': 'John@123', 'role': 'OFFICER', 'department': None, 'ministry': None},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'password': 'Jane@123', 'role': 'OFFICER', 'department': None, 'ministry': None},
            {'username': 'mike_johnson', 'email': 'mike@example.com', 'password': 'Mike@123', 'role': 'OFFICER', 'department': None, 'ministry': None},
            {'username': 'sarah_williams', 'email': 'sarah@example.com', 'password': 'Sarah@123', 'role': 'REPORTING_OFFICER', 'department': 'Finance Department', 'ministry': None},
            {'username': 'robert_brown', 'email': 'robert@example.com', 'password': 'Robert@123', 'role': 'COUNTERSIGNING_OFFICER', 'department': None, 'ministry': 'Ministry of Finance'},
        ]

        created_count = 0
        skipped_count = 0

        for user_data in test_users:
            existing = User.query.filter_by(username=user_data['username']).first()
            if not existing:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    role=user_data['role'],
                    department=user_data.get('department'),
                    ministry=user_data.get('ministry'),
                    is_active=True
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                db.session.flush()
                
                if user_data['role'] in ['OFFICER', 'REPORTING_OFFICER', 'COUNTERSIGNING_OFFICER']:
                    officer = Officer(
                        user_id=user.id,
                        surname=user.username.capitalize(),
                        first_name=user.role.capitalize(),
                        staff_no=f'{user.role[:3]}{user.id}',
                        title='Mr',
                        ministry=user_data.get('ministry') or 'Test Ministry',
                        department=user_data.get('department') or 'Test Department'
                    )
                    db.session.add(officer)
                
                created_count += 1
            else:
                skipped_count += 1

        db.session.commit()
        return jsonify({'success': True, 'message': f'Created {created_count} new users. Skipped {skipped_count} existing users.'})
    except Exception as e:
        logger.error(f"Error seeding users: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@admin_bp.route('/create-user', methods=['POST'])
@login_required
def create_user():
    """Create a new user (API endpoint)"""
    try:
        if not current_user.has_role('ADMIN'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        department = data.get('department')
        ministry = data.get('ministry')
        surname = data.get('surname', '')
        first_name = data.get('first_name', '')
        staff_no = data.get('staff_no', '')

        if not all([username, email, password, role]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        if role == 'REPORTING_OFFICER' and not department:
            return jsonify({'success': False, 'message': 'Department required for Reporting Officer'}), 400

        if role == 'COUNTERSIGNING_OFFICER' and not ministry:
            return jsonify({'success': False, 'message': 'Ministry required for Countersigning Officer'}), 400

        existing = User.query.filter_by(username=username).first()
        if existing:
            return jsonify({'success': False, 'message': 'Username already exists'}), 400

        user = User(
            username=username,
            email=email,
            role=role,
            department=department if role == 'REPORTING_OFFICER' else None,
            ministry=ministry if role == 'COUNTERSIGNING_OFFICER' else None,
            surname=surname or username.capitalize(),
            first_name=first_name or role.capitalize(),
            staff_no=staff_no or f'STAFF{User.query.count() + 1:03d}',
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.flush()
        
        if role in ['OFFICER', 'REPORTING_OFFICER', 'COUNTERSIGNING_OFFICER']:
            officer = Officer(
                user_id=user.id,
                surname=user.surname,
                first_name=user.first_name,
                staff_no=user.staff_no,
                title='Mr',
                ministry=ministry if role == 'COUNTERSIGNING_OFFICER' else 'Test Ministry',
                department=department if role == 'REPORTING_OFFICER' else 'Test Department'
            )
            db.session.add(officer)

        db.session.commit()
        return jsonify({'success': True, 'message': f'User {username} created successfully'})
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@admin_bp.route('/get-user/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """Get user details for editing"""
    if not current_user.has_role('ADMIN'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    return jsonify({
        'success': True,
        'user': {
            'id': user.id, 'username': user.username, 'email': user.email,
            'role': user.role, 'department': user.department, 'ministry': user.ministry,
            'surname': user.surname, 'first_name': user.first_name, 'staff_no': user.staff_no,
            'is_active': user.is_active, 'full_name': user.full_name
        }
    })


@admin_bp.route('/update-user/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """Update user information"""
    try:
        if not current_user.has_role('ADMIN'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        if 'username' in data and data['username']:
            existing = User.query.filter_by(username=data['username']).first()
            if existing and existing.id != user_id:
                return jsonify({'success': False, 'message': 'Username already exists'}), 400
            user.username = data['username']

        if 'email' in data and data['email']:
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                return jsonify({'success': False, 'message': 'Email already exists'}), 400
            user.email = data['email']

        if 'role' in data and data['role']:
            user.role = data['role']

        if 'surname' in data:
            user.surname = data['surname'] if data['surname'] else None
        if 'first_name' in data:
            user.first_name = data['first_name'] if data['first_name'] else None
        if 'staff_no' in data:
            user.staff_no = data['staff_no'] if data['staff_no'] else None
        if 'department' in data:
            user.department = data['department'] if data['department'] else None
        if 'ministry' in data:
            user.ministry = data['ministry'] if data['ministry'] else None

        if 'is_active' in data:
            user.is_active = data['is_active']

        if 'password' in data and data['password'] and data['password'].strip():
            user.set_password(data['password'])

        db.session.commit()

        officer = Officer.query.filter_by(user_id=user.id).first()
        if officer:
            if user.staff_no and user.staff_no != officer.staff_no:
                existing_officer = Officer.query.filter(
                    Officer.staff_no == user.staff_no,
                    Officer.id != officer.id
                ).first()
                if not existing_officer:
                    officer.staff_no = user.staff_no
            
            officer.surname = user.surname or officer.surname
            officer.first_name = user.first_name or officer.first_name
            if user.department:
                officer.department = user.department
            if user.ministry:
                officer.ministry = user.ministry
            
            db.session.commit()

        return jsonify({'success': True, 'message': f'User {user.username} updated successfully', 'user': {
            'id': user.id, 'username': user.username, 'email': user.email,
            'role': user.role, 'department': user.department, 'ministry': user.ministry,
            'surname': user.surname, 'first_name': user.first_name,
            'staff_no': user.staff_no, 'is_active': user.is_active
        }})
        
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@admin_bp.route('/delete-user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    """Delete a user"""
    try:
        if not current_user.has_role('ADMIN'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

        if user_id == current_user.id:
            return jsonify({'success': False, 'message': 'Cannot delete your own account'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        officer = Officer.query.filter_by(user_id=user.id).first()
        if officer:
            db.session.delete(officer)

        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'User deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@admin_bp.route('/delete-report/<int:report_id>', methods=['DELETE'])
@login_required
def delete_report(report_id):
    """Delete a performance report"""
    if not current_user.has_role('ADMIN'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    report = PerformanceReport.query.get_or_404(report_id)
    assessment = Assessment.query.filter_by(report_id=report_id).first()
    if assessment:
        db.session.delete(assessment)
    db.session.delete(report)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Report deleted successfully'})


@admin_bp.route('/reset-report-status/<int:report_id>', methods=['POST'])
@login_required
def reset_report_status(report_id):
    """Reset report status to draft"""
    if not current_user.has_role('ADMIN'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    report = PerformanceReport.query.get_or_404(report_id)
    report.status = 'DRAFT'
    report.final_status = 'PENDING_REPORTING'
    report.submitted_at = None
    report.reporting_approved_at = None
    report.reporting_approved_by = None
    report.countersigning_approved_at = None
    report.countersigning_approved_by = None
    report.reporting_comments = None
    report.countersigning_comments = None
    report.rejection_reason = None
    
    if request.json and request.json.get('delete_assessment'):
        assessment = Assessment.query.filter_by(report_id=report_id).first()
        if assessment:
            db.session.delete(assessment)
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Report status reset to DRAFT'})


@admin_bp.route('/download-user-template', methods=['GET'])
@login_required
def download_user_template():
    """Download CSV template for bulk upload"""
    if not current_user.has_role('ADMIN'):
        flash('Access denied', 'danger')
        return redirect(url_for('reports.dashboard'))
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['username', 'email', 'password', 'role', 'department', 'ministry', 'surname', 'first_name', 'staff_no'])
    writer.writerow(['john_doe', 'john@example.com', 'password123', 'OFFICER', '', '', 'Doe', 'John', 'STF001'])
    writer.writerow(['reporting_officer', 'ro@example.com', 'password123', 'REPORTING_OFFICER', 'Digital Economy and Innovation', '', 'Smith', 'Robert', 'RO001'])
    writer.writerow(['countersigning_officer', 'co@example.com', 'password123', 'COUNTERSIGNING_OFFICER', '', 'Ministry of Digital Economy', 'Johnson', 'Mary', 'CO001'])
    
    response = Response(output.getvalue(), mimetype='text/csv',
                      headers={'Content-Disposition': 'attachment; filename=user_upload_template.csv'})
    return response


@admin_bp.route('/bulk-upload-users', methods=['POST'])
@login_required
def bulk_upload_users():
    """Process bulk upload of users from CSV"""
    if not current_user.has_role('ADMIN'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        file = request.files.get('csv_file')
        if not file:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        
        skip_existing = request.form.get('skip_existing') == 'true'
        content = file.read().decode('utf-8')
        csv_reader = csv.DictReader(StringIO(content))
        
        created_users = []
        skipped_users = []
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):
            username = row.get('username', '').strip()
            email = row.get('email', '').strip()
            password = row.get('password', '').strip()
            role = row.get('role', '').strip().upper()
            department = row.get('department', '').strip()
            ministry = row.get('ministry', '').strip()
            surname = row.get('surname', '').strip()
            first_name = row.get('first_name', '').strip()
            staff_no = row.get('staff_no', '').strip()
            
            if not username or not email or not password or not role:
                errors.append(f"Row {row_num}: Missing required fields")
                continue
            
            valid_roles = ['OFFICER', 'REPORTING_OFFICER', 'COUNTERSIGNING_OFFICER', 'HR', 'ADMIN']
            if role not in valid_roles:
                errors.append(f"Row {row_num}: Invalid role '{role}'")
                continue
            
            if role == 'REPORTING_OFFICER' and not department:
                errors.append(f"Row {row_num}: Department required for Reporting Officer")
                continue
            
            if role == 'COUNTERSIGNING_OFFICER' and not ministry:
                errors.append(f"Row {row_num}: Ministry required for Countersigning Officer")
                continue
            
            existing = User.query.filter_by(username=username).first()
            if existing:
                if skip_existing:
                    skipped_users.append(username)
                    continue
                else:
                    errors.append(f"Row {row_num}: Username '{username}' already exists")
                    continue
            
            user = User(
                username=username, email=email, role=role,
                department=department if role == 'REPORTING_OFFICER' else None,
                ministry=ministry if role == 'COUNTERSIGNING_OFFICER' else None,
                surname=surname or username.capitalize(),
                first_name=first_name or role.capitalize(),
                staff_no=staff_no or f'STAFF{row_num:03d}',
                is_active=True
            )
            user.set_password(password)
            db.session.add(user)
            db.session.flush()
            
            if role in ['OFFICER', 'REPORTING_OFFICER', 'COUNTERSIGNING_OFFICER']:
                officer = Officer(
                    user_id=user.id, surname=user.surname, first_name=user.first_name,
                    staff_no=user.staff_no, title='Mr',
                    ministry=ministry if role == 'COUNTERSIGNING_OFFICER' else 'Test Ministry',
                    department=department if role == 'REPORTING_OFFICER' else 'Test Department'
                )
                db.session.add(officer)
            
            created_users.append(username)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully created {len(created_users)} users. Skipped {len(skipped_users)} existing users.',
            'created_users': created_users,
            'skipped_users': skipped_users,
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f"Error in bulk upload: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}', 'errors': [str(e)]}), 500


@admin_bp.route('/save-background-logo', methods=['POST'])
@login_required
def save_background_logo():
    """Save background logo settings from URL"""
    if not current_user.has_role('ADMIN'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        logo_url = data.get('logo_url', '')
        logo_opacity = data.get('logo_opacity', 0.1)
        
        # Save to database
        logo_setting = SystemSetting.query.filter_by(key='background_logo_url').first()
        if not logo_setting:
            logo_setting = SystemSetting(
                key='background_logo_url',
                value=logo_url,
                description='Background watermark logo URL'
            )
            db.session.add(logo_setting)
        else:
            logo_setting.value = logo_url
        
        opacity_setting = SystemSetting.query.filter_by(key='background_logo_opacity').first()
        if not opacity_setting:
            opacity_setting = SystemSetting(
                key='background_logo_opacity',
                value=str(logo_opacity),
                description='Background watermark logo opacity (0-1)'
            )
            db.session.add(opacity_setting)
        else:
            opacity_setting.value = str(logo_opacity)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Settings saved successfully'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving background logo: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@admin_bp.route('/upload-background-logo', methods=['POST'])
@login_required
def upload_background_logo():
    """Upload background logo from device"""
    if not current_user.has_role('ADMIN'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        # Check if file was uploaded
        if 'logo_file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        
        file = request.files['logo_file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': f'File type not allowed. Use: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save file with secure filename
        filename = secure_filename(f"background_logo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Create URL for the uploaded file
        logo_url = f"/static/uploads/{filename}"
        logo_opacity = float(request.form.get('logo_opacity', 0.1))
        
        # Save to database
        logo_setting = SystemSetting.query.filter_by(key='background_logo_url').first()
        if not logo_setting:
            logo_setting = SystemSetting(
                key='background_logo_url',
                value=logo_url,
                description='Background watermark logo URL'
            )
            db.session.add(logo_setting)
        else:
            logo_setting.value = logo_url
        
        opacity_setting = SystemSetting.query.filter_by(key='background_logo_opacity').first()
        if not opacity_setting:
            opacity_setting = SystemSetting(
                key='background_logo_opacity',
                value=str(logo_opacity),
                description='Background watermark logo opacity (0-1)'
            )
            db.session.add(opacity_setting)
        else:
            opacity_setting.value = str(logo_opacity)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Logo uploaded successfully'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error uploading logo: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500