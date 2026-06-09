from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.performance_report import PerformanceReport
from app.models.assessment import Assessment
from app.assessments import assessments_bp
from datetime import datetime

@assessments_bp.route('/pending')
@login_required
def pending_assessments():
    """Show reports pending assessment"""
    
    pending_reports = []
    
    # For Reporting Officers - show reports pending their assessment
    if current_user.has_role('REPORTING_OFFICER'):
        pending_reports = PerformanceReport.query.filter(
            PerformanceReport.target_reporting_officer_id == current_user.id,
            PerformanceReport.status == 'SUBMITTED',
            PerformanceReport.final_status == 'PENDING_REPORTING'
        ).all()
        
    # For Countersigning Officers - show reports pending their countersignature
    elif current_user.has_role('COUNTERSIGNING_OFFICER'):
        pending_reports = PerformanceReport.query.filter(
            PerformanceReport.target_countersigning_officer_id == current_user.id,
            PerformanceReport.status == 'REVIEWED',
            PerformanceReport.final_status == 'PENDING_COUNTERSIGNING'
        ).all()
        
    # For Admins - show all pending reports
    elif current_user.has_role('ADMIN'):
        pending_reports = PerformanceReport.query.filter(
            PerformanceReport.final_status.in_(['PENDING_REPORTING', 'PENDING_COUNTERSIGNING'])
        ).all()
    else:
        flash('Access denied. Only Reporting Officers, Countersigning Officers, and Admins can access this page.', 'danger')
        return redirect(url_for('reports.dashboard'))
    
    return render_template('assessments/pending.html', reports=pending_reports, user_role=current_user.role)


@assessments_bp.route('/assess/<int:report_id>', methods=['GET', 'POST'])
@login_required
def assess_report(report_id):
    """Assess a report as Reporting Officer or Countersigning Officer"""
    report = PerformanceReport.query.get_or_404(report_id)
    
    # Determine user role and permission
    is_reporting_officer = (report.target_reporting_officer_id == current_user.id and 
                           current_user.has_role('REPORTING_OFFICER'))
    is_countersigning_officer = (report.target_countersigning_officer_id == current_user.id and 
                                 current_user.has_role('COUNTERSIGNING_OFFICER'))
    is_admin = current_user.has_role('ADMIN')
    
    if not (is_reporting_officer or is_countersigning_officer or is_admin):
        flash('You are not authorized to assess this report.', 'danger')
        return redirect(url_for('assessments.pending_assessments'))
    
    # Get or create assessment
    assessment = Assessment.query.filter_by(report_id=report_id).first()
    if not assessment:
        assessment = Assessment(report_id=report_id)
        db.session.add(assessment)
    
    if request.method == 'POST':
        try:
            # For Reporting Officer assessment
            if is_reporting_officer or is_admin:
                # Update assessment grades
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
                
                # Update report status
                report.status = 'REVIEWED'
                report.final_status = 'PENDING_COUNTERSIGNING'
                report.reporting_approved_at = datetime.utcnow()
                report.reporting_approved_by = current_user.id
                report.reporting_comments = request.form.get('reporting_comments')
                
                flash('Assessment submitted successfully! Report sent to Countersigning Officer.', 'success')
                
            # For Countersigning Officer countersignature
            elif is_countersigning_officer:
                report.status = 'FINALIZED'
                report.final_status = 'FINALIZED'
                report.countersigning_approved_at = datetime.utcnow()
                report.countersigning_approved_by = current_user.id
                report.countersigning_comments = request.form.get('countersigning_comments')
                
                flash('Report countersigned successfully! Report is now finalized.', 'success')
            
            db.session.commit()
            return redirect(url_for('assessments.pending_assessments'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting assessment: {str(e)}', 'danger')
    
    return render_template('assessments/assess.html', report=report, assessment=assessment, user_role=current_user.role)