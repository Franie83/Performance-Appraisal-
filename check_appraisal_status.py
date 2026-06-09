from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal
from app.models.user import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='john_doe').first()
    if user:
        appraisal = YearlyAppraisal.query.filter_by(user_id=user.id, appraisal_year=2026).first()
        if appraisal:
            print(f'Appraisal ID: {appraisal.id}')
            print(f'Status: {appraisal.status}')
            print(f'Officer Agrees: {appraisal.officer_agrees}')
            print(f'Section B Total: {appraisal.section_b_total}')
            print(f'Total Score: {appraisal.total_score}/80')
            print(f'Rating: {appraisal.rating}')
        else:
            print('No appraisal found')
    else:
        print('User john_doe not found')