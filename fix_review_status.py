# fix_review_status.py
from app import create_app, db
from app.models.quarterly_plan import QuarterlyGoal

app = create_app()
with app.app_context():
    print("=" * 60)
    print("FIXING REVIEW STATUS")
    print("=" * 60)
    
    # Find the goal with SUBMITTED review but review_completed_by set
    goal = QuarterlyGoal.query.get(4)
    
    if goal:
        print(f"\nGoal ID: {goal.id}")
        print(f"Description: {goal.goal_description}")
        print(f"Review Status: {goal.review_status}")
        print(f"Review Completed By (before): {goal.review_completed_by}")
        
        # Clear review_completed_by for SUBMITTED reviews
        if goal.review_status == 'SUBMITTED':
            goal.review_completed_by = None
            db.session.commit()
            print(f"Review Completed By (after): {goal.review_completed_by}")
            print(f"\n✅ Fixed! The review will now appear in RO's pending actions.")
        else:
            print(f"\n⚠️ Review status is {goal.review_status}, not SUBMITTED")
    else:
        print("Goal ID 4 not found")