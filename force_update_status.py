from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal
from app.models.user import User
from datetime import datetime

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='john_doe').first()
    if user:
        appraisal = YearlyAppraisal.query.filter_by(user_id=user.id, appraisal_year=2026).first()
        if appraisal:
            # Update status to OFFICER_RESPONSE
            appraisal.status = 'OFFICER_RESPONSE'
            # Add some sample scores if needed
            appraisal.diligently_executed = 4
            appraisal.delivered_timelines = 4
            appraisal.punctuality_effectiveness = 4
            appraisal.decency_presentability = 4
            appraisal.productivity = 4
            appraisal.communication_skills = 4
            appraisal.team_collaboration = 4
            appraisal.independent_work = 4
            appraisal.openness_to_learning = 4
            appraisal.proactivity_initiative = 4
            appraisal.calculate_section_b_total()
            appraisal.reporting_officer_comments = "Good performance. Keep it up!"
            appraisal.reporting_officer_sent_at = datetime.utcnow()
            
            db.session.commit()
            print(f'✅ Updated appraisal {appraisal.id}')
            print(f'   Status: {appraisal.status}')
            print(f'   Section B Total: {appraisal.section_b_total}')
            print(f'   Comments: {appraisal.reporting_officer_comments}')
            print(f'\n🔗 Officer response link: http://localhost:5000/quarterly/respond-appraisal/{appraisal.id}')
        else:
            print('No appraisal found')
    else:
        print('User not found')