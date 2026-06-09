# debug_appraisal.py
from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal
from app.models.user import User

app = create_app()
with app.app_context():
    print("=" * 60)
    print("DEBUGGING YEARLY APPRAISAL STATUS")
    print("=" * 60)
    
    # Check all appraisals
    appraisals = YearlyAppraisal.query.all()
    print(f"\nTotal Appraisals: {len(appraisals)}")
    
    for a in appraisals:
        user = User.query.get(a.user_id)
        print(f"\n--- Appraisal ID: {a.id} ---")
        print(f"Officer: {user.username if user else 'Unknown'}")
        print(f"Status: {a.status}")
        print(f"Reporting Officer ID: {a.reporting_officer_id}")
        print(f"Section B Total: {a.section_b_total}")
        print(f"Submitted at: {a.submitted_at}")
        print(f"RO Sent at: {a.reporting_officer_sent_at}")
    
    # Check Reporting Officer
    ro = User.query.filter_by(role='REPORTING_OFFICER').first()
    if ro:
        print(f"\n--- Reporting Officer ---")
        print(f"Username: {ro.username}")
        print(f"ID: {ro.id}")
        print(f"Email: {ro.email}")
    
    # Check for any appraisals that should be in OFFICER_RESPONSE
    print("\n--- Appraisals needing RO response ---")
    pending_response = YearlyAppraisal.query.filter_by(status='OFFICER_RESPONSE').all()
    print(f"Count: {len(pending_response)}")
    
    for a in pending_response:
        user = User.query.get(a.user_id)
        print(f"  - {user.username if user else 'Unknown'} (ID: {a.id})")