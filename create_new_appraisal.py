from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal
from app.models.user import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='john_doe').first()
    if user:
        appraisal = YearlyAppraisal(
            user_id=user.id,
            appraisal_year=2026,
            annual_report="This is a test annual report for the quarterly appraisal system.\n\nKey achievements:\n- Completed all quarterly goals successfully\n- Improved team collaboration\n- Exceeded performance targets",
            reasons_for_failure="No major failures. All targets met on time.",
            status='DRAFT'
        )
        db.session.add(appraisal)
        db.session.commit()
        print(f'✅ New yearly appraisal created for {user.username}')
        print(f'   Appraisal ID: {appraisal.id}')
        print(f'   Status: {appraisal.status}')
        print(f'\n🔗 Edit link: http://localhost:5000/quarterly/yearly-appraisal')
    else:
        print('User not found')