# finalize_2025.py
from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal

app = create_app()
with app.app_context():
    # Find the 2025 appraisal
    appraisal = YearlyAppraisal.query.filter_by(appraisal_year=2025).first()
    
    if appraisal:
        print(f"Appraisal ID: {appraisal.id}")
        print(f"Year: {appraisal.appraisal_year}")
        print(f"Current Status: {appraisal.status}")
        
        # Finalize it
        appraisal.status = 'FINALIZED'
        db.session.commit()
        
        print(f"\n✅ Updated Status: {appraisal.status}")
        print(f"🔗 PDF URL: http://localhost:5000/quarterly/export-pdf/{appraisal.id}")
    else:
        print("2025 appraisal not found")