from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    # Delete existing users (optional - clean start)
    User.query.delete()
    db.session.commit()
    
    # Create users
    users = [
        ('admin', 'admin@example.com', 'ADMIN', 'admin123'),
        ('john_doe', 'john@example.com', 'OFFICER', 'password123'),
        ('jane_smith', 'jane@example.com', 'OFFICER', 'password123'),
        ('reporting_officer', 'ro@example.com', 'REPORTING_OFFICER', 'password123'),
        ('countersigning_officer', 'co@example.com', 'COUNTERSIGNING_OFFICER', 'password123'),
        ('hr_officer', 'hr@example.com', 'HR', 'password123'),
    ]
    
    for username, email, role, password in users:
        user = User(username=username, email=email, role=role, is_active=True)
        user.set_password(password)
        db.session.add(user)
        print(f"Created: {username} ({role})")
    
    db.session.commit()
    print("\n✅ All users created successfully!")
    print("\n📋 Login Credentials:")
    print("   admin / admin123")
    print("   john_doe / password123")
    print("   jane_smith / password123")
    print("   reporting_officer / password123")
    print("   countersigning_officer / password123")
    print("   hr_officer / password123")