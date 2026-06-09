# check_goals_status.py
from app import create_app, db
from app.models.quarterly_plan import QuarterlyGoal
from app.models.user import User

app = create_app()
with app.app_context():
    print("=" * 60)
    print("CHECKING ALL QUARTERLY GOALS")
    print("=" * 60)
    
    # Get all goals
    goals = QuarterlyGoal.query.all()
    
    if goals:
        for goal in goals:
            user = User.query.get(goal.user_id)
            print(f"\nGoal ID: {goal.id}")
            print(f"  Owner: {user.username} (Role: {user.role})")
            print(f"  Description: {goal.goal_description}")
            print(f"  Status: {goal.plan_status}")
            print(f"  Quarter: {goal.quarter}")
            print(f"  Year: {goal.planning_year}")
    else:
        print("No goals found in the database")