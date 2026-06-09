from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal
from app.models.user import User

app = create_app()
with app.app_context():
    reporting_officer = User.query.filter_by(username='reporting_officer').first()
    if reporting_officer:
        # Check pending appraisals
        pending = YearlyAppraisal.query.filter(
            YearlyAppraisal.status == 'SUBMITTED',
            YearlyAppraisal.reporting_officer_id == reporting_officer.id
        ).all()
        
        print(f'Reporting Officer: {reporting_officer.username} (ID: {reporting_officer.id})')
        print(f'Found {len(pending)} pending appraisal(s):')
        for a in pending:
            user = User.query.get(a.user_id)
            print(f'  - Appraisal {a.id}: {user.username} - Status: {a.status}')
        
        # Also check unassigned appraisals
        unassigned = YearlyAppraisal.query.filter(
            YearlyAppraisal.status == 'SUBMITTED',
            YearlyAppraisal.reporting_officer_id.is_(None)
        ).all()
        
        if unassigned:
            print(f'\n⚠️ Found {len(unassigned)} unassigned appraisal(s):')
            for a in unassigned:
                user = User.query.get(a.user_id)
                print(f'  - Appraisal {a.id}: {user.username} - No Reporting Officer assigned')