from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal
from app.models.user import User

app = create_app()
with app.app_context():
    # Get users
    officer = User.query.filter_by(username='john_doe').first()
    reporting_officer = User.query.filter_by(username='reporting_officer').first()
    
    if officer and reporting_officer:
        # Get the latest appraisal for john_doe (ID 3)
        appraisal = YearlyAppraisal.query.filter_by(
            user_id=officer.id,
            appraisal_year=2026
        ).order_by(YearlyAppraisal.id.desc()).first()
        
        if appraisal:
            appraisal.reporting_officer_id = reporting_officer.id
            appraisal.status = 'SUBMITTED'
            db.session.commit()
            print(f'✅ Assigned Reporting Officer to appraisal {appraisal.id}')
            print(f'   Reporting Officer: {reporting_officer.username} (ID: {reporting_officer.id})')
            print(f'   Status: {appraisal.status}')
            print(f'\n🔗 Direct link for Reporting Officer:')
            print(f'   http://localhost:5000/quarterly/ro-yearly-appraisal/{appraisal.id}')
        else:
            print('No appraisal found for john_doe')
    else:
        print('User not found')