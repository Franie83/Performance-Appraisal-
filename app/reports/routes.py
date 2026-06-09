from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.performance_report import PerformanceReport
from app.reports import reports_bp
from datetime import datetime
import traceback
import json

# Import unified audit logger
from app.utils.unified_audit_logger import UnifiedAuditLogger

@reports_bp.route('/dashboard')
@login_required
def dashboard():
    users = User.query.all() if current_user.has_role('ADMIN') else []
    return render_template('dashboard.html', user=current_user, users=users)


@reports_bp.route('/create-for-user/<int:user_id>')
@login_required
def create_report_for_user(user_id):
    """Create a report for a specific user (Admin only)"""
    if not current_user.has_role('ADMIN'):
        flash('Access denied', 'danger')
        return redirect(url_for('reports.dashboard'))
    
    user = User.query.get_or_404(user_id)
    # Store the user_id in session to pre-populate the form
    session['admin_create_for_user'] = user_id
    flash(f'Creating report for: {user.full_name or user.username}', 'info')
    return redirect(url_for('reports.create_report'))


@reports_bp.route('/my-reports')
@login_required
def my_reports():
    # Get all users for admin dropdown
    all_users = User.query.all() if current_user.has_role('ADMIN') else []
    
    # Get available years for filtering
    available_years = db.session.query(PerformanceReport.report_year).distinct().order_by(PerformanceReport.report_year.desc()).all()
    available_years = [year[0] for year in available_years if year[0]]
    
    # Admin can view reports for any user via query parameter
    user_id = request.args.get('user_id', type=int)
    
    if user_id and current_user.has_role('ADMIN'):
        # Admin viewing reports for a specific user
        target_user = User.query.get_or_404(user_id)
        reports = PerformanceReport.query.filter_by(user_id=user_id).order_by(PerformanceReport.created_at.desc()).all()
        
        # Apply filters if provided
        year_filter = request.args.get('year')
        status_filter = request.args.get('status')
        search_term = request.args.get('search')
        
        if year_filter:
            reports = [r for r in reports if str(r.report_year) == year_filter]
        if status_filter:
            reports = [r for r in reports if r.status == status_filter]
        if search_term:
            search_term_lower = search_term.lower()
            reports = [r for r in reports if 
                      search_term_lower in (r.division_targets or '').lower() or 
                      search_term_lower in (r.appraiser_targets or '').lower() or
                      search_term_lower in (r.main_duties or '').lower()]
        
        flash(f'Showing reports for: {target_user.full_name or target_user.username}', 'info')
        return render_template('reports/my_reports.html', 
                             reports=reports, 
                             viewing_user=target_user, 
                             is_admin_view=True,
                             all_users=all_users,
                             available_years=available_years)
    
    # Regular user viewing their own reports
    if not current_user.has_role('OFFICER') and not current_user.has_role('REPORTING_OFFICER') and not current_user.has_role('COUNTERSIGNING_OFFICER'):
        flash('Access denied', 'danger')
        return redirect(url_for('reports.dashboard'))
    
    reports = PerformanceReport.query.filter_by(user_id=current_user.id).order_by(PerformanceReport.created_at.desc()).all()
    
    # Apply filters if provided
    year_filter = request.args.get('year')
    status_filter = request.args.get('status')
    search_term = request.args.get('search')
    
    if year_filter:
        reports = [r for r in reports if str(r.report_year) == year_filter]
    if status_filter:
        reports = [r for r in reports if r.status == status_filter]
    if search_term:
        search_term_lower = search_term.lower()
        reports = [r for r in reports if 
                  search_term_lower in (r.division_targets or '').lower() or 
                  search_term_lower in (r.appraiser_targets or '').lower() or
                  search_term_lower in (r.main_duties or '').lower()]
    
    return render_template('reports/my_reports.html', 
                         reports=reports, 
                         viewing_user=current_user, 
                         is_admin_view=False,
                         all_users=all_users,
                         available_years=available_years)


@reports_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_report():
    # Check if Admin is creating for another user
    target_user_id = session.pop('admin_create_for_user', None) if current_user.has_role('ADMIN') else None
    
    if target_user_id:
        # Admin creating report for another user
        target_user = User.query.get(target_user_id)
        if not target_user:
            flash('Target user not found', 'danger')
            return redirect(url_for('reports.dashboard'))
        user_for_report = target_user
        flash(f'Creating report for: {user_for_report.full_name or user_for_report.username}', 'info')
    else:
        # User creating report for themselves
        if not current_user.has_role('OFFICER') and not current_user.has_role('REPORTING_OFFICER') and not current_user.has_role('COUNTERSIGNING_OFFICER'):
            flash('Access denied', 'danger')
            return redirect(url_for('reports.dashboard'))
        user_for_report = current_user
    
    # Get available officers for workflow
    reporting_officers = User.query.filter_by(role='REPORTING_OFFICER', is_active=True).all()
    countersigning_officers = User.query.filter_by(role='COUNTERSIGNING_OFFICER', is_active=True).all()
    
    # Auto-select Reporting Officer based on user's Ministry and Department
    auto_reporting_officer_id = None
    auto_countersigning_officer_id = None
    
    # Find Reporting Officer with same Ministry AND Department
    if user_for_report.ministry and user_for_report.department:
        reporting_officer = User.query.filter(
            User.role == 'REPORTING_OFFICER',
            User.ministry == user_for_report.ministry,
            User.department == user_for_report.department,
            User.is_active == True
        ).first()
        if reporting_officer:
            auto_reporting_officer_id = reporting_officer.id
            print(f"Auto-assigned Reporting Officer: {reporting_officer.username}")
    
    # Find Countersigning Officer with same Ministry only
    if user_for_report.ministry:
        countersigning_officer = User.query.filter(
            User.role == 'COUNTERSIGNING_OFFICER',
            User.ministry == user_for_report.ministry,
            User.is_active == True
        ).first()
        if countersigning_officer:
            auto_countersigning_officer_id = countersigning_officer.id
            print(f"Auto-assigned Countersigning Officer: {countersigning_officer.username}")
    
    if request.method == 'POST':
        try:
            report_year = request.form.get('report_year')
            period_from = request.form.get('period_from')
            period_to = request.form.get('period_to')
            
            # Use selected values from form, or fall back to auto-assigned
            reporting_officer_id = request.form.get('reporting_officer_id') or auto_reporting_officer_id
            countersigning_officer_id = request.form.get('countersigning_officer_id') or auto_countersigning_officer_id
            
            # Create report using direct SQL INSERT
            from sqlalchemy import text
            
            sql = text("""
                INSERT INTO performance_reports (
                    user_id, report_year, period_from, period_to, 
                    division_targets, appraiser_targets, main_duties, constraints_difficulties,
                    target_reporting_officer_id, target_countersigning_officer_id,
                    status, final_status, created_at, updated_at
                ) VALUES (
                    :user_id, :report_year, :period_from, :period_to,
                    :division_targets, :appraiser_targets, :main_duties, :constraints_difficulties,
                    :target_reporting_officer_id, :target_countersigning_officer_id,
                    'DRAFT', 'PENDING_REPORTING', :created_at, :updated_at
                )
            """)
            
            now = datetime.utcnow()
            
            # Parse dates
            period_from_date = datetime.strptime(period_from, '%Y-%m-%d').date()
            period_to_date = datetime.strptime(period_to, '%Y-%m-%d').date()
            
            result = db.session.execute(sql, {
                'user_id': user_for_report.id,
                'report_year': int(report_year),
                'period_from': period_from_date,
                'period_to': period_to_date,
                'division_targets': request.form.get('division_targets', ''),
                'appraiser_targets': request.form.get('appraiser_targets', ''),
                'main_duties': request.form.get('main_duties', ''),
                'constraints_difficulties': request.form.get('constraints_difficulties', ''),
                'target_reporting_officer_id': int(reporting_officer_id) if reporting_officer_id else None,
                'target_countersigning_officer_id': int(countersigning_officer_id) if countersigning_officer_id else None,
                'created_at': now,
                'updated_at': now
            })
            
            db.session.commit()
            report_id = result.lastrowid
            
            if report_id:
                # Update with verification code
                verification_code = f"GEN79A-{report_id:06d}-{report_year}"
                db.session.execute(text("UPDATE performance_reports SET verification_code = :code WHERE id = :id"), 
                                 {'code': verification_code, 'id': report_id})
                db.session.commit()
                
                # Audit log: Report creation
                UnifiedAuditLogger.log_gen79a_create(
                    user=current_user,
                    report_id=report_id,
                    officer_name=user_for_report.full_name or user_for_report.username,
                    report_data={
                        'year': report_year,
                        'period_from': period_from,
                        'period_to': period_to,
                        'reporting_officer_id': reporting_officer_id,
                        'countersigning_officer_id': countersigning_officer_id
                    }
                )
                
                flash('Performance report created successfully!', 'success')
                return redirect(url_for('reports.view_report', report_id=report_id))
            else:
                flash('Failed to create report', 'danger')
                
        except Exception as e:
            db.session.rollback()
            print(f"Error: {traceback.format_exc()}")
            flash(f'Error: {str(e)}', 'danger')
        
        return redirect(url_for('reports.create_report'))
    
    return render_template('reports/create.html', 
                         reporting_officers=reporting_officers, 
                         countersigning_officers=countersigning_officers,
                         auto_reporting_officer_id=auto_reporting_officer_id,
                         auto_countersigning_officer_id=auto_countersigning_officer_id,
                         target_user=user_for_report if target_user_id else None)


@reports_bp.route('/view/<int:report_id>')
@login_required
def view_report(report_id):
    report = PerformanceReport.query.get(report_id)
    if not report:
        flash('Report not found', 'danger')
        return redirect(url_for('reports.my_reports'))
    
    is_owner = report.user_id == current_user.id
    is_admin = current_user.has_role('ADMIN')
    is_assigned_reporting = report.target_reporting_officer_id == current_user.id
    is_assigned_countersigning = report.target_countersigning_officer_id == current_user.id
    
    if not (is_owner or is_admin or is_assigned_reporting or is_assigned_countersigning):
        flash('Access denied', 'danger')
        return redirect(url_for('reports.dashboard'))
    
    return render_template('reports/view.html', report=report)


@reports_bp.route('/export-pdf/<int:report_id>')
@login_required
def export_pdf(report_id):
    """Export report as PDF"""
    report = PerformanceReport.query.get(report_id)
    if not report:
        flash('Report not found', 'danger')
        return redirect(url_for('reports.my_reports'))
    
    # Check permissions
    is_owner = report.user_id == current_user.id
    is_admin = current_user.has_role('ADMIN')
    is_assigned_reporting = report.target_reporting_officer_id == current_user.id
    is_assigned_countersigning = report.target_countersigning_officer_id == current_user.id
    
    if not (is_owner or is_admin or is_assigned_reporting or is_assigned_countersigning):
        flash('Access denied', 'danger')
        return redirect(url_for('reports.dashboard'))
    
    # Get the user (officer) who owns the report
    officer = User.query.get(report.user_id)
    officer_name = officer.full_name or officer.username if officer else f"User ID {report.user_id}"
    
    # Audit log: PDF export
    UnifiedAuditLogger.log(
        user=current_user,
        action='EXPORT',
        entity_type='GEN79A_REPORT',
        entity_id=report.id,
        entity_name=f"Report for {officer_name} - {report.report_year}",
        new_value="PDF exported",
        module='GEN79A'
    )
    
    # Get related data
    staff_user = User.query.get(report.user_id)
    reporting_officer = User.query.get(report.target_reporting_officer_id) if report.target_reporting_officer_id else None
    countersigning_officer = User.query.get(report.target_countersigning_officer_id) if report.target_countersigning_officer_id else None
    
    # Get assessment if exists
    from app.models.assessment import Assessment
    assessment = Assessment.query.filter_by(report_id=report_id).first()
    
    # Generate PDF
    try:
        from app.utils.pdf_generator import ReportPDFGenerator
        pdf_gen = ReportPDFGenerator(report, staff_user, reporting_officer, countersigning_officer, assessment)
        
        filename = f"performance_report_{report.id}_{staff_user.username}.pdf"
        return pdf_gen.download(filename)
    except ImportError as e:
        flash('PDF generation library not installed. Please run: pip install reportlab', 'danger')
        return redirect(url_for('reports.view_report', report_id=report_id))
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'danger')
        return redirect(url_for('reports.view_report', report_id=report_id))


@reports_bp.route('/submit/<int:report_id>', methods=['POST'])
@login_required
def submit_report(report_id):
    report = PerformanceReport.query.get(report_id)
    if not report:
        return jsonify({'success': False, 'message': 'Report not found'})
    
    if report.user_id != current_user.id and not current_user.has_role('ADMIN'):
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    if report.status == 'DRAFT':
        report.status = 'SUBMITTED'
        report.submitted_at = datetime.utcnow()
        db.session.commit()
        
        # Get the user (officer) who owns the report
        officer = User.query.get(report.user_id)
        officer_name = officer.full_name or officer.username if officer else f"User ID {report.user_id}"
        
        # Audit log: Report submission
        UnifiedAuditLogger.log_gen79a_submit(
            user=current_user,
            report_id=report.id,
            officer_name=officer_name
        )
        
        return jsonify({'success': True, 'message': 'Report submitted successfully'})
    
    return jsonify({'success': False, 'message': 'Report cannot be submitted'})


@reports_bp.route('/update/<int:report_id>', methods=['POST'])
@login_required
def update_report(report_id):
    """Update a draft report"""
    report = PerformanceReport.query.get(report_id)
    if not report:
        return jsonify({'success': False, 'message': 'Report not found'})
    
    if report.user_id != current_user.id and not current_user.has_role('ADMIN'):
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    if report.status != 'DRAFT':
        return jsonify({'success': False, 'message': 'Only draft reports can be edited'})
    
    try:
        changes = {}
        
        # Track changes for audit
        old_division_targets = report.division_targets
        new_division_targets = request.form.get('division_targets', '')
        if old_division_targets != new_division_targets:
            changes['division_targets'] = {'old': old_division_targets[:100], 'new': new_division_targets[:100]}
            report.division_targets = new_division_targets
        
        old_appraiser_targets = report.appraiser_targets
        new_appraiser_targets = request.form.get('appraiser_targets', '')
        if old_appraiser_targets != new_appraiser_targets:
            changes['appraiser_targets'] = {'old': old_appraiser_targets[:100], 'new': new_appraiser_targets[:100]}
            report.appraiser_targets = new_appraiser_targets
        
        old_main_duties = report.main_duties
        new_main_duties = request.form.get('main_duties', '')
        if old_main_duties != new_main_duties:
            changes['main_duties'] = {'old': old_main_duties[:100], 'new': new_main_duties[:100]}
            report.main_duties = new_main_duties
        
        old_constraints = report.constraints_difficulties
        new_constraints = request.form.get('constraints_difficulties', '')
        if old_constraints != new_constraints:
            changes['constraints_difficulties'] = {'old': old_constraints[:100], 'new': new_constraints[:100]}
            report.constraints_difficulties = new_constraints
        
        report.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Audit log: Report update
        if changes:
            officer = User.query.get(report.user_id)
            officer_name = officer.full_name or officer.username if officer else f"User ID {report.user_id}"
            UnifiedAuditLogger.log_gen79a_update(
                user=current_user,
                report_id=report.id,
                officer_name=officer_name,
                changes=changes
            )
        
        return jsonify({'success': True, 'message': 'Report updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@reports_bp.route('/delete/<int:report_id>', methods=['POST'])
@login_required
def delete_report(report_id):
    """Delete a draft report"""
    report = PerformanceReport.query.get(report_id)
    if not report:
        return jsonify({'success': False, 'message': 'Report not found'})
    
    if report.user_id != current_user.id and not current_user.has_role('ADMIN'):
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    if report.status != 'DRAFT' and not current_user.has_role('ADMIN'):
        return jsonify({'success': False, 'message': 'Only draft reports can be deleted'})
    
    try:
        report_data = {
            'year': report.report_year,
            'status': report.status,
            'period_from': str(report.period_from),
            'period_to': str(report.period_to)
        }
        
        # Get the user (officer) who owns the report
        officer = User.query.get(report.user_id)
        officer_name = officer.full_name or officer.username if officer else f"User ID {report.user_id}"
        
        # Audit log: Report deletion
        UnifiedAuditLogger.log_gen79a_delete(
            user=current_user,
            report_id=report.id,
            officer_name=officer_name,
            report_data=report_data
        )
        
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Report deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})