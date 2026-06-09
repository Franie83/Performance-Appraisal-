# debug_route.py
from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal
from app.models.user import User

app = create_app()
with app.app_context():
    print("=" * 60)
    print("CHECKING WHAT SHOULD BE IN pending_ps_reviews")
    print("=" * 60)
    
    # Get the permanent_secretary user
    ps = User.query.filter_by(username='permanent_secretary').first()
    
    if ps:
        print(f"\nUser: {ps.username}")
        print(f"Role: {ps.role}")
        
        # Query for PS_REVIEW status
        ps_reviews = YearlyAppraisal.query.filter(
            YearlyAppraisal.status == 'PS_REVIEW'
        ).all()
        
        print(f"\nFound {len(ps_reviews)} appraisal(s) in PS_REVIEW status:")
        for a in ps_reviews:
            print(f"  - ID: {a.id}, Officer: {a.user.username}, Year: {a.appraisal_year}")
        
        # Also check if there are any appraisals that need countersigning
        cs_reviews = YearlyAppraisal.query.filter(
            YearlyAppraisal.status == 'COUNTERSIGNING_REVIEW'
        ).all()
        
        if cs_reviews:
            print(f"\nFound {len(cs_reviews)} in COUNTERSIGNING_REVIEW:")
            for a in cs_reviews:
                print(f"  - ID: {a.id}")
    else:
        print("User not found")