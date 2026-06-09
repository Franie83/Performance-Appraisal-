from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # Delete all existing users (clean slate)
    User.query.delete()
    db.session.commit()
    print("Cleared existing users")
    
    # Create new users
    users_data = [
        ("admin", "admin@example.com", "ADMIN", "admin123"),
        ("john_doe", "john@example.com", "OFFICER", "password123"),
        ("jane_smith", "jane@example.com", "OFFICER", "password123"),
        ("reporting_officer", "ro@example.com", "REPORTING_OFFICER", "password123"),
        ("countersigning_officer", "co@example.com", "COUNTERSIGNING_OFFICER", "password123"),
        ("hr_officer", "hr@example.com", "HR", "password123"),
    ]
    
    for username, email, role, password in users_data:
        user = User(username=username, email=email, role=role, is_active=True)
        user.set_password(password)
        db.session.add(user)
        print(f"Created: {username} ({role})")
    
    db.session.commit()
    
    print("\n" + "="*50)
    print("Users created successfully!")
    print("="*50)
    print("\nLogin credentials:")
    print("  admin / admin123")
    print("  john_doe / password123")
    print("  jane_smith / password123")
    print("  reporting_officer / password123")
    print("  countersigning_officer / password123")
    print("  hr_officer / password123")
    print("="*50)
    
    # Verify
    print("\nVerifying users:")
    for user in User.query.all():
        pwd_check = user.check_password("admin123" if user.username == "admin" else "password123")
        print(f"  {user.username} - {user.role} - Password OK: {pwd_check}")