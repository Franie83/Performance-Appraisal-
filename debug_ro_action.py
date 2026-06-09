# debug_ro_action.py
from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal
from app.models.user import User

app = create_app()
with app.app_context():
    print("=" * 60)
    print("CHECKING REPORTING OFFICER PENDING APPRAISALS")
    print("=" * 60)
    
    # Get the reporting officer
    ro = User.query.filter_by(role='REPORTING_OFFICER').first()
    print(f"\nReporting Officer: {ro.username} (ID: {ro.id})")
    
    # Find appraisals assigned to this RO
    pending = YearlyAppraisal.query.filter(
        YearlyAppraisal.reporting_officer_id == ro.id,
        YearlyAppraisal.status.in_(['SUBMITTED', 'RO_REVIEW'])
    ).all()
    
    print(f"\nPending Appraisals for RO: {len(pending)}")
    
    for a in pending:
        print(f"\n--- Appraisal ID: {a.id} ---")
        print(f"Officer: {a.user.username}")
        print(f"Year: {a.appraisal_year}")
        print(f"Status: {a.status}")
        print(f"Section B Total: {a.section_b_total}")
        print(f"Training Score: {a.training_attendance_score}")
        print(f"Clock-in Score: {a.clock_in_score}")
        print(f"Peer Review Score: {a.peer_review_score}")
        print(f"RO Comments: {a.reporting_officer_comments}")
        print(f"RO Sent At: {a.reporting_officer_sent_at}")
    
    # Also check for any appraisals in OFFICER_RESPONSE state
    officer_response = YearlyAppraisal.query.filter_by(status='OFFICER_RESPONSE').all()
    print(f"\nAppraisals in OFFICER_RESPONSE: {len(officer_response)}")
    for a in officer_response:
        print(f"  - ID: {a.id}, Officer: {a.user.username}, Year: {a.appraisal_year}")