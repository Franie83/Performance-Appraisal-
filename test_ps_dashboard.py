# test_ps_dashboard.py
from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal
from app.models.user import User

app = create_app()
with app.app_context():
    print("=" * 60)
    print("CHECKING PS DASHBOARD QUERY")
    print("=" * 60)
    
    # Get the permanent_secretary user
    ps = User.query.filter_by(username='permanent_secretary').first()
    
    if ps:
        print(f"\nLogged in as: {ps.username}")
        print(f"Role: {ps.role}")
        print(f"Has role 'PERMANENT_SECRETARY': {ps.has_role('PERMANENT_SECRETARY')}")
        
        # This is what the dashboard queries
        pending_ps_reviews = YearlyAppraisal.query.filter(
            YearlyAppraisal.status == 'PS_REVIEW'
        ).all()
        
        print(f"\nFound {len(pending_ps_reviews)} appraisal(s) in PS_REVIEW status:")
        for a in pending_ps_reviews:
            print(f"  - ID: {a.id}, Officer: {a.user.username}, Year: {a.appraisal_year}")
        
        # Also check if any appraisals need countersigning
        cs_review = YearlyAppraisal.query.filter(
            YearlyAppraisal.status == 'COUNTERSIGNING_REVIEW'
        ).all()
        
        if cs_review:
            print(f"\nFound {len(cs_review)} appraisal(s) in COUNTERSIGNING_REVIEW status:")
            for a in cs_review:
                print(f"  - ID: {a.id}, Officer: {a.user.username}")
    else:
        print("User 'permanent_secretary' not found")