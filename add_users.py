from app import create_app, db 
from app.models.user import User 
 
app = create_app() 
with app.app_context(): 
    # Create Reporting Officer 
    if not User.query.filter_by(username='reporting_officer').first(): 
        ro = User(username='reporting_officer', email='ro@example.com', role='REPORTING_OFFICER', is_active=True) 
        ro.set_password('password123') 
        db.session.add(ro) 
        print('Created reporting_officer') 
 
    # Create Countersigning Officer 
    if not User.query.filter_by(username='countersigning_officer').first(): 
        co = User(username='countersigning_officer', email='co@example.com', role='COUNTERSIGNING_OFFICER', is_active=True) 
        co.set_password('password123') 
        db.session.add(co) 
        print('Created countersigning_officer') 
 
    # Create HR Officer 
    if not User.query.filter_by(username='hr_officer').first(): 
        hr = User(username='hr_officer', email='hr@example.com', role='HR', is_active=True) 
        hr.set_password('password123') 
        db.session.add(hr) 
        print('Created hr_officer') 
 
    # Create Regular Officer 
    if not User.query.filter_by(username='john_doe').first(): 
        officer = User(username='john_doe', email='john@example.com', role='OFFICER', is_active=True) 
        officer.set_password('password123') 
        db.session.add(officer) 
        print('Created john_doe') 
 
    db.session.commit() 
    print('\nAll users created successfully!') 
