from app import create_app, db 
from app.models.user import User 
 
app = create_app() 
with app.app_context(): 
    users = [ 
        ('reporting_officer', 'ro@example.com', 'REPORTING_OFFICER', 'Digital Economy and Innovation', None), 
        ('countersigning_officer', 'co@example.com', 'COUNTERSIGNING_OFFICER', None, 'Ministry of Digital Economy'), 
        ('hr_officer', 'hr@example.com', 'HR', None, None), 
        ('john_doe', 'john@example.com', 'OFFICER', None, None), 
        ('jane_smith', 'jane@example.com', 'OFFICER', None, None), 
        ('mike_johnson', 'mike@example.com', 'OFFICER', None, None), 
        ('sarah_williams', 'sarah@example.com', 'REPORTING_OFFICER', 'Finance Department', None), 
        ('robert_brown', 'robert@example.com', 'COUNTERSIGNING_OFFICER', None, 'Ministry of Finance'), 
    ] 
 
    for username, email, role, dept, min_val in users: 
        if not User.query.filter_by(username=username).first(): 
            user = User(username=username, email=email, role=role, department=dept, ministry=min_val, is_active=True) 
            user.set_password('password123') 
            db.session.add(user) 
            print(f'Created {username}') 
 
    admin = User.query.filter_by(username='admin').first() 
    if admin: 
        admin.set_password('Admin123') 
        print('Updated admin password') 
    else: 
        admin = User(username='admin', email='admin@example.com', role='ADMIN', is_active=True) 
        admin.set_password('Admin123') 
        db.session.add(admin) 
        print('Created admin user') 
 
    db.session.commit() 
    print('All users created successfully!') 
