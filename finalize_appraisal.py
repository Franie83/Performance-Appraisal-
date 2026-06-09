from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal
from datetime import datetime

app = create_app()
with app.app_context():
    appraisal = YearlyAppraisal.query.get(4)
    
    if appraisal:
        print(f"Appraisal ID: {appraisal.id}")
        print(f"Current Status: {appraisal.status}")
        
        # Finalize the appraisal
        appraisal.status = 'FINALIZED'
        appraisal.finalized_at = datetime.utcnow()
        appraisal.ps_review_completed = True
        appraisal.ps_review_date = datetime.utcnow()
        appraisal.ps_comments = "Finalized by Permanent Secretary"
        
        db.session.commit()
        
        print(f"\n✅ Status updated to: {appraisal.status}")
        print(f"✅ Finalized at: {appraisal.finalized_at}")
        print(f"\n🔗 PDF Download URL: http://localhost:5000/quarterly/export-pdf/4")
    else:
        print("Appraisal not found")