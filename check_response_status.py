# check_response_status.py
from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal
from app.models.user import User
from datetime import datetime

app = create_app()
with app.app_context():
    # Find the appraisal
    appraisal = YearlyAppraisal.query.filter_by(id=3).first()
    
    if appraisal:
        print("=" * 60)
        print("APPRAISAL STATUS AFTER OFFICER RESPONSE")
        print("=" * 60)
        print(f"Appraisal ID: {appraisal.id}")
        print(f"Officer: {appraisal.user.username}")
        print(f"Status: {appraisal.status}")
        print(f"Officer Agrees: {appraisal.officer_agrees}")
        print(f"Officer Comments: {appraisal.officer_comments}")
        print(f"Officer Response At: {appraisal.officer_response_at}")
        print(f"PS Review Completed: {appraisal.ps_review_completed}")
        print(f"Countersigning Officer ID: {appraisal.countersigning_officer_id}")
        print("=" * 60)
        
        # Check for PS officer
        ps_officer = User.query.filter_by(role='PERMANENT_SECRETARY').first()
        if ps_officer:
            print(f"\n✅ PS Officer exists: {ps_officer.username} (ID: {ps_officer.id})")
        else:
            print("\n⚠️ No PERMANENT_SECRETARY found - appraisal should finalize directly")
    else:
        print("Appraisal not found")