# check_users.py
from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    print("=" * 60)
    print("USER ROLES CHECK")
    print("=" * 60)
    
    all_users = User.query.all()
    for user in all_users:
        print(f"Username: {user.username}")
        print(f"  Role: {user.role}")
        print(f"  Has role 'PERMANENT_SECRETARY': {user.has_role('PERMANENT_SECRETARY')}")
        print(f"  Active: {user.is_active}")
        print("-" * 40)