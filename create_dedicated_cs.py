# create_dedicated_cs.py
from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    # Check if a dedicated CS officer exists
    cs = User.query.filter_by(username='cs_officer').first()
    
    if not cs:
        cs = User(
            username='cs_officer',
            email='cs@example.com',
            role='COUNTERSIGNING_OFFICER',
            is_active=True
        )
        cs.set_password('password123')
        db.session.add(cs)
        db.session.commit()
        print("✅ Created dedicated Countersigning Officer:")
        print("   Username: cs_officer")
        print("   Password: password123")
    else:
        print(f"Countersigning Officer already exists: {cs.username}")
    
    # List all users with their roles
    print("\nAll users and their roles:")
    all_users = User.query.all()
    for user in all_users:
        print(f"  - {user.username}: {user.role}")