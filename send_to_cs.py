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
            if appraisal.officer_agrees == False:
                appraisal.status = 'COUNTERSIGN_REVIEW'
                db.session.commit()
                print(f'✅ Appraisal {appraisal.id} sent to Countersigning Officer')
                print(f'   Status: {appraisal.status}')
                print(f'   Disagreement Reason: {appraisal.officer_disagreement_reason}')
            elif appraisal.officer_agrees == True:
                appraisal.status = 'FINALIZED'
                appraisal.finalized_at = datetime.utcnow()
                db.session.commit()
                print(f'✅ Officer agreed! Appraisal {appraisal.id} is FINALIZED')
            else:
                print(f'Status: {appraisal.status} - No response yet')
        else:
            print('No appraisal found')
    else:
        print('User not found')