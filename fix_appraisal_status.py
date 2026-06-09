# fix_appraisal_status.py
from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal
from datetime import datetime

app = create_app()
with app.app_context():
    # Find the appraisal for john_doe (ID 3)
    appraisal = YearlyAppraisal.query.filter_by(id=3).first()
    
    if appraisal:
        print(f"Current status: {appraisal.status}")
        print(f"Reporting Officer ID: {appraisal.reporting_officer_id}")
        print(f"Section B Total: {appraisal.section_b_total}")
        
        # If status is still SUBMITTED but should be OFFICER_RESPONSE
        if appraisal.status == 'SUBMITTED' and appraisal.section_b_total > 0:
            appraisal.status = 'OFFICER_RESPONSE'
            appraisal.reporting_officer_sent_at = datetime.utcnow()
            db.session.commit()
            print(f"✅ Updated status to: {appraisal.status}")
        else:
            print(f"Status is already: {appraisal.status}")
    else:
        print("Appraisal not found")