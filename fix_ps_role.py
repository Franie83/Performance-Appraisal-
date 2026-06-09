# fix_ps_role.py
from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    print("=" * 60)
    print("FIXING PERMANENT SECRETARY ROLE")
    print("=" * 60)
    
    # Find the permanent_secretary user
    ps = User.query.filter_by(username='permanent_secretary').first()
    
    if ps:
        print(f"\nCurrent user details:")
        print(f"  Username: {ps.username}")
        print(f"  Current Role: {ps.role}")
        print(f"  Is Active: {ps.is_active}")
        
        # Change role to COUNTERSIGNING_OFFICER
        ps.role = 'COUNTERSIGNING_OFFICER'
        db.session.commit()
        
        print(f"\n✅ Updated role to: {ps.role}")
        print(f"\nYou can now login as:")
        print(f"  Username: permanent_secretary")
        print(f"  Password: password123")
        print(f"  Role: COUNTERSIGNING_OFFICER")
    else:
        print("❌ User 'permanent_secretary' not found")
        
        # List all users
        print("\nAvailable users:")
        all_users = User.query.all()
        for user in all_users:
            print(f"  - {user.username} (Role: {user.role})")