from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com', role='ADMIN', is_active=True)
        admin.set_password('admin123')
        db.session.add(admin)
        print('Admin user created')
    else:
        print('Admin user already exists')
    
    # Create test users only if they don't exist
    test_users = [
        ('john_doe', 'john@example.com', 'OFFICER', 'password123'),
        ('jane_smith', 'jane@example.com', 'OFFICER', 'password123'),
        ('reporting_officer', 'ro@example.com', 'REPORTING_OFFICER', 'password123'),
        ('countersigning_officer', 'co@example.com', 'COUNTERSIGNING_OFFICER', 'password123'),
    ]
    
    created_count = 0
    for username, email, role, pwd in test_users:
        existing = User.query.filter_by(username=username).first()
        if not existing:
            user = User(username=username, email=email, role=role, is_active=True)
            user.set_password(pwd)
            db.session.add(user)
            created_count += 1
            print(f'Created user: {username}')
        else:
            print(f'User already exists: {username}')
    
    db.session.commit()
    
    print('=' * 50)
    print(f'Users created: {created_count}')
    print('=' * 50)
    print('Login credentials:')
    print('  Admin: admin / admin123')
    print('  Officers: john_doe, jane_smith / password123')
    print('  Reporting Officer: reporting_officer / password123')
    print('  Countersigning Officer: countersigning_officer / password123')
    print('=' * 50)