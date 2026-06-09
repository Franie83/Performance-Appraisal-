# finalize_now.py
from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal
from datetime import datetime

app = create_app()
with app.app_context():
    # Find appraisal for john_doe
    appraisal = YearlyAppraisal.query.filter_by(id=3).first()
    
    if appraisal:
        print("=" * 50)
        print("Current Appraisal Status")
        print("=" * 50)
        print(f"Appraisal ID: {appraisal.id}")
        print(f"Officer: {appraisal.user.username}")
        print(f"Status: {appraisal.status}")
        print(f"Officer Agrees: {appraisal.officer_agrees}")
        print(f"Section B Total: {appraisal.section_b_total}")
        print("=" * 50)
        
        # Update to finalized
        appraisal.status = 'FINALIZED'
        appraisal.finalized_at = datetime.utcnow()
        db.session.commit()
        
        print("\n✅ Appraisal Finalized!")
        print(f"New Status: {appraisal.status}")
        print(f"Finalized At: {appraisal.finalized_at}")
        print(f"\n🔗 Download PDF: http://localhost:5000/quarterly/export-pdf/{appraisal.id}")
    else:
        print("Appraisal ID 3 not found")