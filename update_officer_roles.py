from app import create_app, db 
from app.models.user import User 
 
app = create_app() 
with app.app_context(): 
    # Find or create reporting officer 
    ro = User.query.filter_by(username='reporting_officer').first() 
    if ro: 
        ro.department = 'Digital Economy and Innovation' 
        print(f'Updated reporting_officer: department={ro.department}') 
    else: 
        ro = User(username='reporting_officer', email='ro@example.com', role='REPORTING_OFFICER', is_active=True, department='Digital Economy and Innovation') 
        ro.set_password('password123') 
        db.session.add(ro) 
        print('Created reporting_officer with department') 
 
    # Find or create countersigning officer 
    co = User.query.filter_by(username='countersigning_officer').first() 
    if co: 
        co.ministry = 'Ministry of Digital Economy' 
        print(f'Updated countersigning_officer: ministry={co.ministry}') 
    else: 
        co = User(username='countersigning_officer', email='co@example.com', role='COUNTERSIGNING_OFFICER', is_active=True, ministry='Ministry of Digital Economy') 
        co.set_password('password123') 
        db.session.add(co) 
        print('Created countersigning_officer with ministry') 
 
    db.session.commit() 
    print('Done!') 
