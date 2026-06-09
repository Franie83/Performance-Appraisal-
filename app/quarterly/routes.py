from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.quarterly_plan import QuarterlyGoal, YearlyAppraisal, PlanStatus, ReviewStatus
from app.quarterly import quarterly_bp
from datetime import datetime, date
import traceback
import logging
import json

logger = logging.getLogger(__name__)

# Import audit logger
from app.utils.audit_logger import AuditLogger

@quarterly_bp.route('/dashboard')
@login_required
def dashboard():
    """Quarterly Appraisal Dashboard"""
    current_year = datetime.now().year
    
    quarterly_goals = QuarterlyGoal.query.filter_by(
        user_id=current_user.id
    ).order_by(QuarterlyGoal.planning_year.desc(), QuarterlyGoal.quarter).all()
    
    logger.info(f"User {current_user.username} has {len(quarterly_goals)} total goals")
    for goal in quarterly_goals:
        logger.info(f"Goal ID: {goal.id}, Year: {goal.planning_year}, Q{goal.quarter}: {goal.goal_description[:50]} - Status: {goal.plan_status}")
    
    all_yearly_appraisals = YearlyAppraisal.query.filter_by(
        user_id=current_user.id
    ).order_by(YearlyAppraisal.appraisal_year.desc()).all() if current_user.has_role('OFFICER') else []
    
    yearly_appraisal = YearlyAppraisal.query.filter_by(
        user_id=current_user.id,
        appraisal_year=current_year
    ).first()
    
    if not yearly_appraisal and current_user.has_role('OFFICER'):
        yearly_appraisal = YearlyAppraisal(
            user_id=current_user.id,
            appraisal_year=current_year,
            status='DRAFT'
        )
        db.session.add(yearly_appraisal)
        db.session.commit()
        logger.info(f"Auto-created yearly appraisal for {current_user.username}")
        
        reporting_officer = User.query.filter_by(role='REPORTING_OFFICER').first()
        if reporting_officer:
            yearly_appraisal.reporting_officer_id = reporting_officer.id
            db.session.commit()
            logger.info(f"Auto-assigned Reporting Officer {reporting_officer.username} to {current_user.username}")
        
        all_yearly_appraisals = YearlyAppraisal.query.filter_by(
            user_id=current_user.id
        ).order_by(YearlyAppraisal.appraisal_year.desc()).all()
    
    pending_plan_approvals = []
    pending_reviews = []
    pending_appraisals = []
    
    if current_user.has_role('REPORTING_OFFICER') or current_user.has_role('ADMIN'):
        pending_plan_approvals = QuarterlyGoal.query.filter(
            QuarterlyGoal.plan_status == PlanStatus.SUBMITTED
        ).all()
        
        pending_reviews = QuarterlyGoal.query.filter(
            QuarterlyGoal.review_status == ReviewStatus.SUBMITTED,
            QuarterlyGoal.review_completed_by.is_(None)
        ).all()
        
        pending_appraisals = YearlyAppraisal.query.filter(
            YearlyAppraisal.reporting_officer_id == current_user.id,
            YearlyAppraisal.status.in_(['SUBMITTED', 'RO_REVIEW'])
        ).all()
        
        logger.info(f"RO {current_user.username} has {len(pending_plan_approvals)} pending goals, {len(pending_reviews)} pending reviews, {len(pending_appraisals)} pending appraisals")
    
    pending_ps_reviews = []
    if current_user.role == 'COUNTERSIGNING_OFFICER' or current_user.role == 'PERMANENT_SECRETARY' or current_user.has_role('PERMANENT_SECRETARY'):
        pending_ps_reviews = YearlyAppraisal.query.filter(
            YearlyAppraisal.status == 'PS_REVIEW'
        ).all()
        print(f"🔍 {current_user.username} found {len(pending_ps_reviews)} pending yearly appraisals")
    
    pending_cs_approvals = []
    if current_user.role == 'COUNTERSIGNING_OFFICER' or current_user.has_role('COUNTERSIGNING_OFFICER'):
        pending_cs_approvals = QuarterlyGoal.query.filter(
            QuarterlyGoal.plan_status == 'PENDING_CS_APPROVAL'
        ).all()
        print(f"🔍 CS {current_user.username} found {len(pending_cs_approvals)} pending goal approvals")
    
    pending_cs_reviews = []
    if current_user.role == 'COUNTERSIGNING_OFFICER' or current_user.has_role('COUNTERSIGNING_OFFICER'):
        pending_cs_reviews = QuarterlyGoal.query.filter(
            QuarterlyGoal.review_status == 'PENDING_CS_REVIEW'
        ).all()
        print(f"🔍 CS {current_user.username} found {len(pending_cs_reviews)} pending review approvals")
    
    return render_template('quarterly/dashboard.html',
                         quarterly_goals=quarterly_goals,
                         yearly_appraisal=yearly_appraisal,
                         all_yearly_appraisals=all_yearly_appraisals,
                         pending_plan_approvals=pending_plan_approvals,
                         pending_reviews=pending_reviews,
                         pending_appraisals=pending_appraisals,
                         pending_ps_reviews=pending_ps_reviews,
                         pending_cs_approvals=pending_cs_approvals,
                         pending_cs_reviews=pending_cs_reviews,
                         current_year=current_year)

@quarterly_bp.route('/quarter-summary/<int:quarter>')
@login_required
def quarter_summary(quarter):
    current_year = datetime.now().year
    goals = QuarterlyGoal.query.filter_by(
        user_id=current_user.id,
        planning_year=current_year,
        quarter=quarter,
        review_status='REVIEWED'
    ).all()
    return render_template('quarterly/quarter_summary.html', goals=goals, quarter=quarter, current_year=current_year)

@quarterly_bp.route('/view-review/<int:goal_id>')
@login_required
def view_review(goal_id):
    goal = QuarterlyGoal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id and not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    return render_template('quarterly/view_review_detail.html', goal=goal)

@quarterly_bp.route('/view-reviews')
@login_required
def view_reviews():
    current_year = datetime.now().year
    reviews = QuarterlyGoal.query.filter_by(
        user_id=current_user.id,
        planning_year=current_year,
        review_status='REVIEWED'
    ).order_by(QuarterlyGoal.quarter).all()
    return render_template('quarterly/view_reviews.html', reviews=reviews, current_year=current_year)

@quarterly_bp.route('/plan-goal', methods=['GET', 'POST'])
@login_required
def plan_goal():
    if request.method == 'POST':
        try:
            current_year = datetime.now().year
            goal = QuarterlyGoal(
                user_id=current_user.id,
                planning_year=current_year,
                quarter=request.form.get('quarter'),
                goal_description=request.form.get('goal_description'),
                priority=request.form.get('priority', 3),
                success_criteria=request.form.get('success_criteria'),
                plan_status=PlanStatus.DRAFT
            )
            db.session.add(goal)
            db.session.commit()
            logger.info(f"Goal created for {current_user.username}: Year={current_year}, Q={goal.quarter}")
            flash('Goal created successfully!', 'success')
            return redirect(url_for('quarterly.dashboard'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating goal: {str(e)}")
            flash(f'Error: {str(e)}', 'danger')
    return render_template('quarterly/plan_goal.html', current_year=datetime.now().year)

@quarterly_bp.route('/edit-goal/<int:goal_id>', methods=['GET', 'POST'])
@login_required
def edit_goal(goal_id):
    goal = QuarterlyGoal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id and not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    if goal.plan_status not in ['DRAFT', 'MODIFIED']:
        flash('This goal cannot be edited because it has already been approved.', 'warning')
        return redirect(url_for('quarterly.dashboard'))
    if request.method == 'POST':
        try:
            goal.quarter = request.form.get('quarter')
            goal.goal_description = request.form.get('goal_description')
            goal.priority = request.form.get('priority')
            goal.success_criteria = request.form.get('success_criteria')
            goal.plan_status = PlanStatus.DRAFT
            goal.plan_submitted_at = None
            goal.plan_approved_at = None
            goal.plan_approved_by = None
            goal.plan_modifications = None
            db.session.commit()
            flash('Goal updated successfully! You can now resubmit for approval.', 'success')
            return redirect(url_for('quarterly.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating goal: {str(e)}', 'danger')
    return render_template('quarterly/edit_goal.html', goal=goal, current_year=datetime.now().year)

@quarterly_bp.route('/submit-goal/<int:goal_id>', methods=['POST'])
@login_required
def submit_goal(goal_id):
    try:
        goal = QuarterlyGoal.query.get_or_404(goal_id)
        if goal.user_id != current_user.id:
            flash('Unauthorized', 'danger')
            return redirect(url_for('quarterly.dashboard'))
        goal.plan_status = PlanStatus.SUBMITTED
        goal.plan_submitted_at = datetime.utcnow()
        db.session.commit()
        flash('Goal submitted for approval successfully!', 'success')
        return redirect(url_for('quarterly.dashboard'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('quarterly.dashboard'))

@quarterly_bp.route('/approve-goal/<int:goal_id>', methods=['GET', 'POST'])
@login_required
def approve_goal(goal_id):
    goal = QuarterlyGoal.query.get_or_404(goal_id)
    is_reporting_officer = current_user.has_role('REPORTING_OFFICER') or current_user.has_role('ADMIN')
    is_countersigning_officer = current_user.role == 'COUNTERSIGNING_OFFICER' or current_user.has_role('COUNTERSIGNING_OFFICER')
    if not (is_reporting_officer or is_countersigning_officer):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    if is_reporting_officer and goal.plan_status == 'SUBMITTED':
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'approve':
                goal.plan_status = 'PENDING_CS_APPROVAL'
                goal.plan_approved_at = datetime.utcnow()
                goal.plan_approved_by = current_user.id
                flash('✅ Goal approved! Sent to Countersigning Officer for final approval.', 'success')
            elif action == 'modify':
                goal.plan_status = 'MODIFIED'
                goal.plan_modifications = request.form.get('modifications')
                flash('📝 Modification requested. Goal returned to officer.', 'warning')
            db.session.commit()
            return redirect(url_for('quarterly.dashboard'))
        return render_template('quarterly/approve_goal.html', goal=goal, approval_level='RO')
    elif is_countersigning_officer and goal.plan_status == 'PENDING_CS_APPROVAL':
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'approve':
                goal.plan_status = 'APPROVED'
                goal.cs_approved = True
                goal.cs_approved_at = datetime.utcnow()
                goal.cs_approved_by = current_user.id
                goal.cs_comments = request.form.get('cs_comments')
                flash('✅ Goal finalized by Countersigning Officer!', 'success')
            elif action == 'return':
                goal.plan_status = 'SUBMITTED'
                goal.cs_approved = False
                goal.cs_approved_at = None
                goal.cs_approved_by = None
                goal.cs_comments = request.form.get('cs_comments')
                flash('Goal returned to Reporting Officer for review.', 'warning')
            db.session.commit()
            return redirect(url_for('quarterly.dashboard'))
        return render_template('quarterly/approve_goal_cs.html', goal=goal)
    else:
        flash(f'Cannot approve goal in current state: {goal.plan_status}', 'warning')
        return redirect(url_for('quarterly.dashboard'))

@quarterly_bp.route('/quarterly-review/<int:quarter>', methods=['GET', 'POST'])
@login_required
def quarterly_review(quarter):
    current_year = datetime.now().year
    goals = QuarterlyGoal.query.filter_by(
        user_id=current_user.id,
        planning_year=current_year,
        quarter=quarter
    ).all()
    if request.method == 'POST':
        try:
            for goal in goals:
                if goal.review_status in ['PENDING', 'SUBMITTED']:
                    goal.achievements = request.form.get(f'achievements_{goal.id}')
                    goal.challenges = request.form.get(f'challenges_{goal.id}')
                    goal.reasons_for_failure = request.form.get(f'reasons_{goal.id}')
                    goal.recovery_plan = request.form.get(f'recovery_{goal.id}')
                    goal.review_status = ReviewStatus.SUBMITTED
                    goal.review_submitted_at = datetime.utcnow()
            db.session.commit()
            flash(f'Q{quarter} review submitted successfully!', 'success')
            return redirect(url_for('quarterly.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    return render_template('quarterly/quarterly_review.html', goals=goals, quarter=quarter)

@quarterly_bp.route('/review-quarterly/<int:goal_id>', methods=['GET', 'POST'])
@login_required
def review_quarterly(goal_id):
    goal = QuarterlyGoal.query.get_or_404(goal_id)
    is_reporting_officer = current_user.has_role('REPORTING_OFFICER') or current_user.has_role('ADMIN')
    is_countersigning_officer = current_user.role == 'COUNTERSIGNING_OFFICER' or current_user.has_role('COUNTERSIGNING_OFFICER')
    if not (is_reporting_officer or is_countersigning_officer):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    if is_reporting_officer and goal.review_status == 'SUBMITTED':
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'approve':
                goal.reporting_officer_comments = request.form.get('comments')
                goal.further_directives = request.form.get('directives')
                goal.quarter_2_adjustments = request.form.get('adjustments')
                goal.review_status = 'PENDING_CS_REVIEW'
                goal.review_completed_at = datetime.utcnow()
                goal.review_completed_by = current_user.id
                db.session.commit()
                flash('✅ Review completed! Sent to Countersigning Officer for final approval.', 'success')
            elif action == 'return':
                goal.reporting_officer_comments = request.form.get('comments')
                goal.review_status = 'PENDING'
                goal.review_submitted_at = None
                db.session.commit()
                flash('📝 Review returned to officer for modification.', 'warning')
            return redirect(url_for('quarterly.dashboard'))
        return render_template('quarterly/review_quarterly.html', goal=goal, approval_level='RO')
    elif is_countersigning_officer and goal.review_status == 'PENDING_CS_REVIEW':
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'approve':
                goal.review_status = 'REVIEWED'
                goal.cs_review_approved = True
                goal.cs_review_approved_at = datetime.utcnow()
                goal.cs_review_approved_by = current_user.id
                goal.cs_review_comments = request.form.get('cs_review_comments')
                flash('✅ Quarterly review finalized by Countersigning Officer!', 'success')
            elif action == 'return':
                goal.review_status = 'SUBMITTED'
                goal.cs_review_comments = request.form.get('cs_review_comments')
                flash('Review returned to Reporting Officer for revision.', 'warning')
            db.session.commit()
            return redirect(url_for('quarterly.dashboard'))
        return render_template('quarterly/review_quarterly_cs.html', goal=goal)
    else:
        flash(f'Cannot review in current state: {goal.review_status}', 'warning')
        return redirect(url_for('quarterly.dashboard'))

@quarterly_bp.route('/yearly-appraisal', methods=['GET', 'POST'])
@login_required
def yearly_appraisal():
    current_year = datetime.now().year
    selected_year = request.args.get('year', type=int) or current_year
    appraisal = YearlyAppraisal.query.filter_by(
        user_id=current_user.id,
        appraisal_year=selected_year
    ).first()
    if not appraisal:
        appraisal = YearlyAppraisal(
            user_id=current_user.id,
            appraisal_year=selected_year,
            status='DRAFT'
        )
        db.session.add(appraisal)
        db.session.commit()
        reporting_officer = User.query.filter_by(role='REPORTING_OFFICER').first()
        if reporting_officer:
            appraisal.reporting_officer_id = reporting_officer.id
            db.session.commit()
            flash(f'Yearly appraisal for {selected_year} created with Reporting Officer assigned.', 'info')
        else:
            flash(f'Yearly appraisal for {selected_year} created. Please contact admin to assign Reporting Officer.', 'warning')
    if request.method == 'POST':
        try:
            appraisal.section_b_work_output = float(request.form.get('section_b_work_output', 0))
            appraisal.section_b_innovation = float(request.form.get('section_b_innovation', 0))
            appraisal.section_b_leadership = float(request.form.get('section_b_leadership', 0))
            appraisal.section_b_teamwork = float(request.form.get('section_b_teamwork', 0))
            appraisal.section_b_communication = float(request.form.get('section_b_communication', 0))
            appraisal.section_b_ethics = float(request.form.get('section_b_ethics', 0))
            section_b_total = (
                appraisal.section_b_work_output +
                appraisal.section_b_innovation +
                appraisal.section_b_leadership +
                appraisal.section_b_teamwork +
                appraisal.section_b_communication +
                appraisal.section_b_ethics
            )
            appraisal.section_b_total = min(section_b_total, 40)
            appraisal.annual_report = request.form.get('annual_report')
            appraisal.reasons_for_failure = request.form.get('reasons_for_failure')
            if 'submit' in request.form:
                if appraisal.section_b_total == 0:
                    flash('Please complete the Section B self-assessment before submitting', 'danger')
                    return redirect(url_for('quarterly.yearly_appraisal', year=selected_year))
                appraisal.status = 'SUBMITTED'
                appraisal.submitted_at = datetime.utcnow()
                flash(f'✅ Yearly appraisal for {selected_year} submitted to Reporting Officer for review!', 'success')
            else:
                flash(f'Draft saved for {selected_year}!', 'info')
            db.session.commit()
            return redirect(url_for('quarterly.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error: {str(e)}', 'danger')
    return render_template('quarterly/yearly_appraisal.html', appraisal=appraisal)

@quarterly_bp.route('/ro-yearly-appraisal/<int:appraisal_id>', methods=['GET', 'POST'])
@login_required
def ro_yearly_appraisal(appraisal_id):
    appraisal = YearlyAppraisal.query.get_or_404(appraisal_id)
    if not (current_user.has_role('REPORTING_OFFICER') or current_user.has_role('ADMIN')):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    if appraisal.reporting_officer_id != current_user.id and not current_user.has_role('ADMIN'):
        flash('This appraisal is not assigned to you', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    if appraisal.status not in ['SUBMITTED', 'RO_REVIEW']:
        flash(f'Cannot assess appraisal in {appraisal.status} status', 'warning')
        return redirect(url_for('quarterly.dashboard'))
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            appraisal.training_attendance_score = int(request.form.get('training_attendance_score', 0))
            appraisal.clock_in_score = int(request.form.get('clock_in_score', 0))
            appraisal.peer_review_score = int(request.form.get('peer_review_score', 0))
            appraisal.diligently_executed = int(request.form.get('diligently_executed', 3))
            appraisal.delivered_timelines = int(request.form.get('delivered_timelines', 3))
            appraisal.punctuality_effectiveness = int(request.form.get('punctuality_effectiveness', 3))
            appraisal.decency_presentability = int(request.form.get('decency_presentability', 3))
            appraisal.productivity = int(request.form.get('productivity', 3))
            appraisal.communication_skills = int(request.form.get('communication_skills', 3))
            appraisal.team_collaboration = int(request.form.get('team_collaboration', 3))
            appraisal.independent_work = int(request.form.get('independent_work', 3))
            appraisal.openness_to_learning = int(request.form.get('openness_to_learning', 3))
            appraisal.proactivity_initiative = int(request.form.get('proactivity_initiative', 3))
            appraisal.calculate_section_b_total()
            appraisal.reporting_officer_comments = request.form.get('comments')
            if action == 'approve':
                appraisal.status = 'OFFICER_RESPONSE'
                appraisal.reporting_officer_sent_at = datetime.utcnow()
                flash('✅ Assessment approved and sent to officer for response!', 'success')
            elif action == 'request_modification':
                appraisal.status = 'MODIFICATION_REQUESTED'
                flash('📝 Modification requested. Appraisal returned to officer.', 'warning')
            db.session.commit()
            return redirect(url_for('quarterly.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error: {str(e)}', 'danger')
    return render_template('quarterly/ro_yearly_appraisal.html', appraisal=appraisal)

@quarterly_bp.route('/respond-appraisal/<int:appraisal_id>', methods=['GET', 'POST'])
@login_required
def respond_appraisal(appraisal_id):
    appraisal = YearlyAppraisal.query.get_or_404(appraisal_id)
    if appraisal.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    if appraisal.status != 'OFFICER_RESPONSE':
        flash(f'Cannot respond to appraisal in {appraisal.status} status', 'warning')
        return redirect(url_for('quarterly.dashboard'))
    section_a_total = (appraisal.training_attendance_score or 0) + (appraisal.clock_in_score or 0) + (appraisal.peer_review_score or 0)
    section_a_total = min(section_a_total, 20)
    section_b_total = appraisal.section_b_total or 0
    section_b_total = min(section_b_total, 40)
    total_score = section_a_total + section_b_total
    total_score = min(total_score, 60)
    if total_score >= 45:
        rating = 'Excellent'
    elif total_score >= 35:
        rating = 'Good'
    elif total_score >= 25:
        rating = 'Satisfactory'
    elif total_score >= 15:
        rating = 'Needs Improvement'
    else:
        rating = 'Poor'
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            if action == 'accept':
                appraisal.officer_agrees = True
                officer_comment = request.form.get('officer_comments', '')
                if hasattr(appraisal, 'officer_comments'):
                    appraisal.officer_comments = officer_comment
                else:
                    appraisal.reporting_officer_comments = (appraisal.reporting_officer_comments or '') + f"\n\n[Officer Response]: {officer_comment}"
                cs_officer = User.query.filter_by(role='COUNTERSIGNING_OFFICER').first()
                if cs_officer:
                    appraisal.countersigning_officer_id = cs_officer.id
                    appraisal.status = 'PS_REVIEW'
                    appraisal.ps_review_completed = False
                    flash('✅ Appraisal sent to Countersigning Officer for final review', 'success')
                else:
                    appraisal.status = 'FINALIZED'
                    appraisal.finalized_at = datetime.utcnow()
                    flash('✅ Appraisal finalized! You can now download the PDF.', 'success')
            elif action == 'disagree':
                appraisal.officer_agrees = False
                disagreement_reason = request.form.get('disagreement_reason', '')
                if hasattr(appraisal, 'officer_disagreement_reason'):
                    appraisal.officer_disagreement_reason = disagreement_reason
                else:
                    appraisal.reporting_officer_comments = f"Officer Disagreement: {disagreement_reason}"
                appraisal.status = 'RO_REVIEW'
                flash('Your disagreement has been recorded. Appraisal returned to Reporting Officer.', 'warning')
            appraisal.officer_response_at = datetime.utcnow()
            db.session.commit()
            if action == 'accept' and appraisal.status == 'FINALIZED':
                return redirect(url_for('quarterly.export_pdf', appraisal_id=appraisal.id))
            return redirect(url_for('quarterly.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error: {str(e)}', 'danger')
    return render_template('quarterly/respond_appraisal.html', 
                         appraisal=appraisal,
                         section_a_total=section_a_total,
                         section_b_total=section_b_total,
                         total_score=total_score,
                         rating=rating)

@quarterly_bp.route('/ps-review/<int:appraisal_id>', methods=['GET', 'POST'])
@login_required
def ps_review(appraisal_id):
    """Permanent Secretary / Countersigning Officer review"""
    appraisal = YearlyAppraisal.query.get_or_404(appraisal_id)
    
    if not (current_user.has_role('ADMIN') or current_user.role == 'PERMANENT_SECRETARY' or current_user.role == 'COUNTERSIGNING_OFFICER'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    
    # Calculate Section A total
    section_a_total = (appraisal.training_attendance_score or 0) + (appraisal.clock_in_score or 0) + (appraisal.peer_review_score or 0)
    section_a_total = min(section_a_total, 20)
    section_b_total = appraisal.section_b_total or 0
    section_b_total = min(section_b_total, 40)
    total_score = section_a_total + section_b_total
    total_score = min(total_score, 60)
    
    # Calculate rating
    if total_score >= 45:
        rating = 'Excellent'
    elif total_score >= 35:
        rating = 'Good'
    elif total_score >= 25:
        rating = 'Satisfactory'
    elif total_score >= 15:
        rating = 'Needs Improvement'
    else:
        rating = 'Poor'
    
    if request.method == 'POST':
        try:
            # If re-evaluation is requested, update the scores
            if request.form.get('re_evaluate') == 'yes':
                appraisal.diligently_executed = int(request.form.get('diligently_executed', 3))
                appraisal.delivered_timelines = int(request.form.get('delivered_timelines', 3))
                appraisal.punctuality_effectiveness = int(request.form.get('punctuality_effectiveness', 3))
                appraisal.decency_presentability = int(request.form.get('decency_presentability', 3))
                appraisal.productivity = int(request.form.get('productivity', 3))
                appraisal.communication_skills = int(request.form.get('communication_skills', 3))
                appraisal.team_collaboration = int(request.form.get('team_collaboration', 3))
                appraisal.independent_work = int(request.form.get('independent_work', 3))
                appraisal.openness_to_learning = int(request.form.get('openness_to_learning', 3))
                appraisal.proactivity_initiative = int(request.form.get('proactivity_initiative', 3))
                appraisal.calculate_section_b_total()
                # Recalculate totals after update
                section_b_total = appraisal.section_b_total
                total_score = section_a_total + section_b_total
                if total_score >= 45:
                    rating = 'Excellent'
                elif total_score >= 35:
                    rating = 'Good'
                elif total_score >= 25:
                    rating = 'Satisfactory'
                elif total_score >= 15:
                    rating = 'Needs Improvement'
                else:
                    rating = 'Poor'
            
            action = request.form.get('action')
            
            if action == 'approve':
                # ========== FIX: Save total_score and rating ==========
                appraisal.total_score = total_score
                appraisal.rating = rating
                appraisal.status = 'FINALIZED'
                appraisal.finalized_at = datetime.utcnow()
                flash('✅ Appraisal finalized successfully!', 'success')
            elif action == 'return':
                appraisal.status = 'RO_REVIEW'
                flash('Appraisal returned to Reporting Officer for revision', 'warning')
            
            appraisal.ps_review_completed = True
            appraisal.ps_review_date = datetime.utcnow()
            appraisal.ps_comments = request.form.get('ps_comments')
            db.session.commit()
            
            return redirect(url_for('quarterly.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('quarterly/ps_review.html', 
                         appraisal=appraisal,
                         section_a_total=section_a_total,
                         section_b_total=section_b_total,
                         total_score=total_score,
                         rating=rating)

# ============ ADMIN ROUTES WITH AUDIT LOGGING ============

@quarterly_bp.route('/admin-approve-goal/<int:goal_id>')
@login_required
def admin_approve_goal(goal_id):
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    goal = QuarterlyGoal.query.get_or_404(goal_id)
    goal.plan_status = 'APPROVED'
    goal.plan_approved_at = datetime.utcnow()
    goal.plan_approved_by = current_user.id
    goal.cs_approved = True
    goal.cs_approved_at = datetime.utcnow()
    goal.cs_approved_by = current_user.id
    goal.cs_comments = f"Admin override approval by {current_user.username}"
    db.session.commit()
    AuditLogger.log(
        user=current_user,
        action='APPROVE',
        entity_type='GOAL',
        entity_id=goal.id,
        entity_name=goal.goal_description[:50],
        new_value=f"Status changed to APPROVED by Admin"
    )
    flash(f'✅ Goal "{goal.goal_description[:50]}" approved by Admin!', 'success')
    return redirect(url_for('quarterly.dashboard'))

@quarterly_bp.route('/admin-reject-goal/<int:goal_id>')
@login_required
def admin_reject_goal(goal_id):
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    goal = QuarterlyGoal.query.get_or_404(goal_id)
    goal.plan_status = 'MODIFIED'
    goal.plan_modifications = f"Rejected by Admin ({current_user.username}). Please review and resubmit."
    db.session.commit()
    AuditLogger.log(
        user=current_user,
        action='REJECT',
        entity_type='GOAL',
        entity_id=goal.id,
        entity_name=goal.goal_description[:50],
        new_value=f"Goal rejected, status changed to MODIFIED"
    )
    flash(f'⚠️ Goal "{goal.goal_description[:50]}" has been rejected. User can edit and resubmit.', 'warning')
    return redirect(url_for('quarterly.dashboard'))

@quarterly_bp.route('/admin-delete-goal/<int:goal_id>')
@login_required
def admin_delete_goal(goal_id):
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    goal = QuarterlyGoal.query.get_or_404(goal_id)
    goal_description = goal.goal_description[:50]
    AuditLogger.log(
        user=current_user,
        action='DELETE',
        entity_type='GOAL',
        entity_id=goal.id,
        entity_name=goal_description,
        old_value=f"Goal: {goal_description}, Status: {goal.plan_status}"
    )
    db.session.delete(goal)
    db.session.commit()
    flash(f'🗑️ Goal "{goal_description}" has been deleted by Admin.', 'info')
    return redirect(url_for('quarterly.dashboard'))

@quarterly_bp.route('/admin-approve-appraisal/<int:appraisal_id>')
@login_required
def admin_approve_appraisal(appraisal_id):
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    appraisal = YearlyAppraisal.query.get_or_404(appraisal_id)
    appraisal.status = 'FINALIZED'
    appraisal.finalized_at = datetime.utcnow()
    appraisal.ps_review_completed = True
    appraisal.ps_review_date = datetime.utcnow()
    appraisal.ps_comments = f"Admin override approval by {current_user.username}"
    db.session.commit()
    AuditLogger.log(
        user=current_user,
        action='APPROVE',
        entity_type='APPRAISAL',
        entity_id=appraisal.id,
        entity_name=f"{appraisal.user.username} - {appraisal.appraisal_year}",
        new_value=f"Appraisal finalized by Admin"
    )
    flash(f'✅ Appraisal for {appraisal.appraisal_year} finalized by Admin!', 'success')
    return redirect(url_for('quarterly.dashboard'))

@quarterly_bp.route('/admin-delete-appraisal/<int:appraisal_id>')
@login_required
def admin_delete_appraisal(appraisal_id):
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    appraisal = YearlyAppraisal.query.get_or_404(appraisal_id)
    appraisal_year = appraisal.appraisal_year
    AuditLogger.log(
        user=current_user,
        action='DELETE',
        entity_type='APPRAISAL',
        entity_id=appraisal.id,
        entity_name=f"{appraisal.user.username} - {appraisal_year}",
        old_value=f"Status: {appraisal.status}, Score: {appraisal.total_score}"
    )
    db.session.delete(appraisal)
    db.session.commit()
    flash(f'🗑️ Appraisal for {appraisal_year} has been deleted by Admin.', 'info')
    return redirect(url_for('quarterly.dashboard'))

# ============ ADVANCED ADMIN ROUTES WITH AUDIT LOGGING ============

@quarterly_bp.route('/admin/manage-users')
@login_required
def admin_manage_users():
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    users = User.query.all()
    return render_template('quarterly/admin_manage_users.html', users=users)

@quarterly_bp.route('/admin/create-user', methods=['GET', 'POST'])
@login_required
def admin_create_user():
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        existing = User.query.filter_by(username=username).first()
        if existing:
            flash('Username already exists', 'danger')
        else:
            user = User(username=username, email=email, role=role, is_active=True)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            AuditLogger.log_user_create(
                user=current_user,
                created_by=current_user,
                new_user_data={'id': user.id, 'username': username, 'email': email, 'role': role}
            )
            flash(f'User {username} created successfully!', 'success')
            return redirect(url_for('quarterly.admin_manage_users'))
    return render_template('quarterly/admin_create_user.html')

@quarterly_bp.route('/admin/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        try:
            changes = {}
            new_username = request.form.get('username')
            if user.username != new_username:
                changes['username'] = {'old': user.username, 'new': new_username}
                user.username = new_username
            new_email = request.form.get('email')
            if user.email != new_email:
                changes['email'] = {'old': user.email, 'new': new_email}
                user.email = new_email
            new_role = request.form.get('role')
            if user.role != new_role:
                changes['role'] = {'old': user.role, 'new': new_role}
                user.role = new_role
            new_password = request.form.get('password')
            if new_password:
                changes['password'] = 'Password changed'
                user.set_password(new_password)
            new_surname = request.form.get('surname', '')
            if (user.surname or '') != new_surname:
                changes['surname'] = {'old': user.surname or '', 'new': new_surname}
                user.surname = new_surname
            new_first_name = request.form.get('first_name', '')
            if (user.first_name or '') != new_first_name:
                changes['first_name'] = {'old': user.first_name or '', 'new': new_first_name}
                user.first_name = new_first_name
            new_other_names = request.form.get('other_names', '')
            if (user.other_names or '') != new_other_names:
                changes['other_names'] = {'old': user.other_names or '', 'new': new_other_names}
                user.other_names = new_other_names
            new_title = request.form.get('title', '')
            if (user.title or '') != new_title:
                changes['title'] = {'old': user.title or '', 'new': new_title}
                user.title = new_title
            new_staff_no = request.form.get('staff_no', '')
            if (user.staff_no or '') != new_staff_no:
                changes['staff_no'] = {'old': user.staff_no or '', 'new': new_staff_no}
                user.staff_no = new_staff_no
            new_ministry = request.form.get('ministry', '')
            if (user.ministry or '') != new_ministry:
                changes['ministry'] = {'old': user.ministry or '', 'new': new_ministry}
                user.ministry = new_ministry
            new_department = request.form.get('department', '')
            if (user.department or '') != new_department:
                changes['department'] = {'old': user.department or '', 'new': new_department}
                user.department = new_department
            new_division = request.form.get('division', '')
            if (user.division or '') != new_division:
                changes['division'] = {'old': user.division or '', 'new': new_division}
                user.division = new_division
            new_branch = request.form.get('branch', '')
            if (user.branch or '') != new_branch:
                changes['branch'] = {'old': user.branch or '', 'new': new_branch}
                user.branch = new_branch
            new_section = request.form.get('section', '')
            if (user.section or '') != new_section:
                changes['section'] = {'old': user.section or '', 'new': new_section}
                user.section = new_section
            new_is_active = request.form.get('is_active') == '1'
            if user.is_active != new_is_active:
                changes['is_active'] = {'old': user.is_active, 'new': new_is_active}
                user.is_active = new_is_active
            db.session.commit()
            if changes:
                AuditLogger.log_user_update(
                    user=current_user,
                    updated_by=current_user,
                    user_id=user.id,
                    username=user.username,
                    changes=changes
                )
                flash(f'User {user.username} updated successfully!', 'success')
            else:
                flash('No changes were made to the user.', 'info')
            return redirect(url_for('quarterly.admin_manage_users'))
        except Exception as e:
            db.session.rollback()
            print(f"Error updating user: {str(e)}")
            import traceback
            traceback.print_exc()
            flash(f'Error updating user: {str(e)}', 'danger')
    return render_template('quarterly/admin_edit_user.html', user=user)

@quarterly_bp.route('/admin/delete-user/<int:user_id>')
@login_required
def admin_delete_user(user_id):
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    user = User.query.get_or_404(user_id)
    if user.username == 'admin':
        flash('Cannot delete admin user', 'danger')
    else:
        user_data = user.to_dict()
        AuditLogger.log_user_delete(
            user=current_user,
            deleted_by=current_user,
            user_id=user.id,
            username=user.username,
            user_data=user_data
        )
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} deleted successfully!', 'success')
    return redirect(url_for('quarterly.admin_manage_users'))

@quarterly_bp.route('/admin/manage-goals')
@login_required
def admin_manage_goals():
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    goals = QuarterlyGoal.query.order_by(QuarterlyGoal.id.desc()).all()
    users = User.query.all()
    return render_template('quarterly/admin_manage_goals.html', goals=goals, users=users)

@quarterly_bp.route('/admin/create-goal', methods=['GET', 'POST'])
@login_required
def admin_create_goal():
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        planning_year = request.form.get('planning_year')
        quarter = request.form.get('quarter')
        goal_description = request.form.get('goal_description')
        priority = request.form.get('priority', 3)
        success_criteria = request.form.get('success_criteria')
        goal = QuarterlyGoal(
            user_id=user_id,
            planning_year=planning_year,
            quarter=quarter,
            goal_description=goal_description,
            priority=priority,
            success_criteria=success_criteria,
            plan_status='APPROVED' if request.form.get('auto_approve') else 'DRAFT'
        )
        db.session.add(goal)
        db.session.commit()
        target_user = User.query.get(user_id)
        AuditLogger.log(
            user=current_user,
            action='CREATE',
            entity_type='GOAL',
            entity_id=goal.id,
            entity_name=goal_description[:50],
            new_value=f"Goal for {target_user.username} - Q{quarter} {planning_year}"
        )
        flash('Goal created successfully!', 'success')
        return redirect(url_for('quarterly.admin_manage_goals'))
    users = User.query.all()
    return render_template('quarterly/admin_create_goal.html', users=users)

@quarterly_bp.route('/admin/edit-goal/<int:goal_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_goal(goal_id):
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    goal = QuarterlyGoal.query.get_or_404(goal_id)
    if request.method == 'POST':
        changes = {}
        old_description = goal.goal_description
        new_description = request.form.get('goal_description')
        if old_description != new_description:
            changes['goal_description'] = {'old': old_description[:50], 'new': new_description[:50]}
            goal.goal_description = new_description
        old_quarter = goal.quarter
        new_quarter = int(request.form.get('quarter'))
        if old_quarter != new_quarter:
            changes['quarter'] = {'old': old_quarter, 'new': new_quarter}
            goal.quarter = new_quarter
        old_priority = goal.priority
        new_priority = int(request.form.get('priority'))
        if old_priority != new_priority:
            changes['priority'] = {'old': old_priority, 'new': new_priority}
            goal.priority = new_priority
        goal.success_criteria = request.form.get('success_criteria')
        goal.plan_status = request.form.get('plan_status')
        db.session.commit()
        if changes:
            AuditLogger.log(
                user=current_user,
                action='UPDATE',
                entity_type='GOAL',
                entity_id=goal.id,
                entity_name=goal.goal_description[:50],
                changes=json.dumps(changes)
            )
        flash('Goal updated successfully!', 'success')
        return redirect(url_for('quarterly.admin_manage_goals'))
    return render_template('quarterly/admin_edit_goal.html', goal=goal)

@quarterly_bp.route('/admin/delete-goal-adv/<int:goal_id>')
@login_required
def admin_delete_goal_adv(goal_id):
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    goal = QuarterlyGoal.query.get_or_404(goal_id)
    AuditLogger.log(
        user=current_user,
        action='DELETE',
        entity_type='GOAL',
        entity_id=goal.id,
        entity_name=goal.goal_description[:50],
        old_value=f"Status: {goal.plan_status}, Quarter: {goal.quarter}"
    )
    db.session.delete(goal)
    db.session.commit()
    flash('Goal deleted successfully!', 'success')
    return redirect(url_for('quarterly.admin_manage_goals'))

@quarterly_bp.route('/admin/bulk-approve-goals', methods=['POST'])
@login_required
def admin_bulk_approve_goals():
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    goal_ids = request.form.getlist('goal_ids')
    approved_count = 0
    for goal_id in goal_ids:
        goal = QuarterlyGoal.query.get(goal_id)
        if goal:
            goal.plan_status = 'APPROVED'
            goal.cs_approved = True
            goal.cs_approved_at = datetime.utcnow()
            goal.cs_approved_by = current_user.id
            approved_count += 1
    db.session.commit()
    AuditLogger.log(
        user=current_user,
        action='BULK_APPROVE',
        entity_type='GOAL',
        entity_name=f"{approved_count} goals",
        new_value=f"Bulk approved {approved_count} goals"
    )
    flash(f'{approved_count} goals approved successfully!', 'success')
    return redirect(url_for('quarterly.admin_manage_goals'))

@quarterly_bp.route('/admin/manage-reviews')
@login_required
def admin_manage_reviews():
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    goals = QuarterlyGoal.query.filter(
        QuarterlyGoal.review_status.in_(['SUBMITTED', 'PENDING_CS_REVIEW', 'REVIEWED'])
    ).order_by(QuarterlyGoal.review_submitted_at.desc()).all()
    return render_template('quarterly/admin_manage_reviews.html', goals=goals)

@quarterly_bp.route('/admin/bulk-approve-reviews', methods=['POST'])
@login_required
def admin_bulk_approve_reviews():
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    review_ids = request.form.getlist('review_ids')
    approved_count = 0
    for review_id in review_ids:
        goal = QuarterlyGoal.query.get(review_id)
        if goal:
            goal.review_status = 'REVIEWED'
            goal.cs_review_approved = True
            goal.cs_review_approved_at = datetime.utcnow()
            goal.cs_review_approved_by = current_user.id
            approved_count += 1
    db.session.commit()
    AuditLogger.log(
        user=current_user,
        action='BULK_APPROVE',
        entity_type='REVIEW',
        entity_name=f"{approved_count} reviews",
        new_value=f"Bulk approved {approved_count} quarterly reviews"
    )
    flash(f'{approved_count} reviews approved successfully!', 'success')
    return redirect(url_for('quarterly.admin_manage_reviews'))

@quarterly_bp.route('/admin/manage-appraisals')
@login_required
def admin_manage_appraisals():
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    appraisals = YearlyAppraisal.query.order_by(YearlyAppraisal.appraisal_year.desc()).all()
    return render_template('quarterly/admin_manage_appraisals.html', appraisals=appraisals)

@quarterly_bp.route('/admin/create-appraisal', methods=['GET', 'POST'])
@login_required
def admin_create_appraisal():
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        appraisal_year = request.form.get('appraisal_year')
        status = request.form.get('status', 'DRAFT')
        appraisal = YearlyAppraisal(
            user_id=user_id,
            appraisal_year=appraisal_year,
            status=status
        )
        db.session.add(appraisal)
        db.session.commit()
        target_user = User.query.get(user_id)
        AuditLogger.log(
            user=current_user,
            action='CREATE',
            entity_type='APPRAISAL',
            entity_id=appraisal.id,
            entity_name=f"{target_user.username} - {appraisal_year}",
            new_value=f"Appraisal created with status {status}"
        )
        flash(f'Appraisal for {appraisal_year} created successfully!', 'success')
        return redirect(url_for('quarterly.admin_manage_appraisals'))
    users = User.query.all()
    return render_template('quarterly/admin_create_appraisal.html', users=users)

@quarterly_bp.route('/admin/delete-appraisal-adv/<int:appraisal_id>')
@login_required
def admin_delete_appraisal_adv(appraisal_id):
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    appraisal = YearlyAppraisal.query.get_or_404(appraisal_id)
    AuditLogger.log(
        user=current_user,
        action='DELETE',
        entity_type='APPRAISAL',
        entity_id=appraisal.id,
        entity_name=f"{appraisal.user.username} - {appraisal.appraisal_year}",
        old_value=f"Status: {appraisal.status}, Score: {appraisal.total_score}"
    )
    db.session.delete(appraisal)
    db.session.commit()
    flash('Appraisal deleted successfully!', 'success')
    return redirect(url_for('quarterly.admin_manage_appraisals'))

@quarterly_bp.route('/admin/clear-test-data')
@login_required
def admin_clear_test_data():
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    users_to_delete = User.query.filter(User.username != 'admin').count()
    non_admin = User.query.filter(User.username != 'admin').all()
    for user in non_admin:
        db.session.delete(user)
    db.session.commit()
    AuditLogger.log(
        user=current_user,
        action='CLEAR_DATA',
        entity_type='SYSTEM',
        entity_name="Test Data",
        old_value=f"Deleted {users_to_delete} users and their associated data"
    )
    flash('All test data cleared! Please run setup scripts to recreate test users.', 'warning')
    return redirect(url_for('quarterly.dashboard'))

@quarterly_bp.route('/admin/export-all-data')
@login_required
def admin_export_all_data():
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    import json
    AuditLogger.log(
        user=current_user,
        action='EXPORT',
        entity_type='SYSTEM',
        entity_name="All Data",
        new_value="Full system data export"
    )
    data = {
        'users': [],
        'quarterly_goals': [],
        'yearly_appraisals': []
    }
    for user in User.query.all():
        data['users'].append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active
        })
    for goal in QuarterlyGoal.query.all():
        data['quarterly_goals'].append({
            'id': goal.id,
            'user_id': goal.user_id,
            'planning_year': goal.planning_year,
            'quarter': goal.quarter,
            'goal_description': goal.goal_description,
            'plan_status': goal.plan_status,
            'review_status': goal.review_status
        })
    for appraisal in YearlyAppraisal.query.all():
        data['yearly_appraisals'].append({
            'id': appraisal.id,
            'user_id': appraisal.user_id,
            'appraisal_year': appraisal.appraisal_year,
            'status': appraisal.status,
            'total_score': appraisal.total_score
        })
    response = jsonify(data)
    response.headers['Content-Disposition'] = 'attachment; filename=appraisal_export.json'
    return response

@quarterly_bp.route('/admin/system-stats')
@login_required
def admin_system_stats():
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    stats = {
        'total_users': User.query.count(),
        'total_goals': QuarterlyGoal.query.count(),
        'approved_goals': QuarterlyGoal.query.filter_by(plan_status='APPROVED').count(),
        'pending_goals': QuarterlyGoal.query.filter_by(plan_status='SUBMITTED').count(),
        'total_reviews': QuarterlyGoal.query.filter(QuarterlyGoal.review_status != 'PENDING').count(),
        'completed_reviews': QuarterlyGoal.query.filter_by(review_status='REVIEWED').count(),
        'total_appraisals': YearlyAppraisal.query.count(),
        'finalized_appraisals': YearlyAppraisal.query.filter_by(status='FINALIZED').count()
    }
    return render_template('quarterly/admin_system_stats.html', stats=stats)

@quarterly_bp.route('/admin/audit-trail')
@login_required
def admin_audit_trail():
    if not current_user.has_role('ADMIN'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    from app.models.audit_log import AuditLog
    page = request.args.get('page', 1, type=int)
    action_filter = request.args.get('action', '')
    entity_filter = request.args.get('entity_type', '')
    module_filter = request.args.get('module', '')
    query = AuditLog.query
    if action_filter:
        query = query.filter_by(action=action_filter)
    if entity_filter:
        query = query.filter_by(entity_type=entity_filter)
    if module_filter:
        query = query.filter(AuditLog.module == module_filter)
    logs = query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=50, error_out=False)
    return render_template('quarterly/admin_audit_trail.html', 
                         logs=logs, 
                         action_filter=action_filter, 
                         entity_filter=entity_filter,
                         module_filter=module_filter)

@quarterly_bp.route('/export-pdf/<int:appraisal_id>')
@login_required
def export_pdf(appraisal_id):
    appraisal = YearlyAppraisal.query.get_or_404(appraisal_id)
    if appraisal.user_id != current_user.id and not current_user.has_role('ADMIN') and not current_user.has_role('REPORTING_OFFICER'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    if appraisal.status != 'FINALIZED':
        flash('PDF can only be generated for finalized appraisals', 'warning')
        return redirect(url_for('quarterly.dashboard'))
    try:
        from app.utils.pdf_quarterly import QuarterlyPDFGenerator
        pdf_gen = QuarterlyPDFGenerator(appraisal)
        filename = f"quarterly_appraisal_{appraisal.user.username}_{appraisal.appraisal_year}.pdf"
        return pdf_gen.download(filename)
    except ImportError as e:
        flash('PDF generation library not installed. Please run: pip install reportlab', 'danger')
        return redirect(url_for('quarterly.dashboard'))
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'danger')
        return redirect(url_for('quarterly.dashboard'))