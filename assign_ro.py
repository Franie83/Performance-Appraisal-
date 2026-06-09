from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal
from app.models.user import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='john_doe').first()
    reporting_officer = User.query.filter_by(username='reporting_officer').first()
    
    if user and reporting_officer:
        appraisal = YearlyAppraisal.query.filter_by(user_id=user.id, appraisal_year=2026).first()
        if appraisal:
            appraisal.reporting_officer_id = reporting_officer.id
            appraisal.status = 'SUBMITTED'
            db.session.commit()
            print(f'✅ Assigned Reporting Officer {reporting_officer.username} (ID: {reporting_officer.id}) to appraisal {appraisal.id}')
            print(f'Status set to: {appraisal.status}')
        else:
            print('No appraisal found')
    else:
        print('User or Reporting Officer not found')