from app import create_app, db
from app.models.quarterly_plan import QuarterlyGoal

app = create_app()
with app.app_context():
    # Update any APPROVED goals to maintain existing behavior
    # (They stay as APPROVED since they were already finalized)
    print("Goal workflow updated. Existing approved goals remain APPROVED.")