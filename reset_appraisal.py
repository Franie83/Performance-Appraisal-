from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal
from app.models.user import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='john_doe').first()
    if user:
        # Delete existing appraisal
        deleted = YearlyAppraisal.query.filter_by(user_id=user.id, appraisal_year=2026).delete()
        db.session.commit()
        print(f'✅ Deleted {deleted} existing appraisal(s) for {user.username}')
        print(f'You can now create a new yearly appraisal.')
    else:
        print('User not found')