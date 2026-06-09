# check_review_status.py
from app import create_app, db
from app.models.quarterly_plan import QuarterlyGoal

app = create_app()
with app.app_context():
    print("=" * 60)
    print("CHECKING QUARTERLY REVIEW STATUS")
    print("=" * 60)
    
    # Find the goal with pending review
    goals = QuarterlyGoal.query.all()
    
    for goal in goals:
        print(f"\nGoal ID: {goal.id}")
        print(f"  Description: {goal.goal_description}")
        print(f"  Quarter: {goal.quarter}")
        print(f"  Plan Status: {goal.plan_status}")
        print(f"  Review Status: {goal.review_status}")
        print(f"  Review Submitted At: {goal.review_submitted_at}")
        print(f"  Review Completed By: {goal.review_completed_by}")