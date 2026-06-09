from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal
from app.models.user import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='john_doe').first()
    if user:
        appraisal = YearlyAppraisal.query.filter_by(user_id=user.id, appraisal_year=2026).order_by(YearlyAppraisal.id.desc()).first()
        if appraisal:
            print(f'Appraisal ID: {appraisal.id}')
            print(f'Status: {appraisal.status}')
            print(f'Reporting Officer ID: {appraisal.reporting_officer_id}')
            print(f'Submitted at: {appraisal.submitted_at}')
            
            # Check if reporting officer exists
            ro = User.query.get(appraisal.reporting_officer_id)
            print(f'Reporting Officer: {ro.username if ro else "Not found"}')
        else:
            print('No appraisal found')
    else:
        print('User not found')