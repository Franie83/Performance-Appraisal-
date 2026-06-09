from app import create_app, db 
from app.models.user import User 
from app.models.officer import Officer 
 
app = create_app() 
with app.app_context(): 
    users = User.query.all() 
    created = 0 
 
    for user in users: 
        # Skip admin user 
        if user.username == 'admin': 
            print(f'Skipping admin user') 
            continue 
 
        # Check if already has officer profile 
        existing = Officer.query.filter_by(user_id=user.id).first() 
        if existing: 
            print(f'Officer profile already exists for {user.username}') 
            continue 
 
        # Create officer profile 
        officer = Officer( 
            user_id=user.id, 
            surname=user.username.capitalize(), 
            first_name=user.role.capitalize(), 
            staff_no=f'{user.role[:3]}{user.id}', 
            title='Mr' 
        ) 
 
        # Set ministry for Countersigning Officer 
        if user.role == 'COUNTERSIGNING_OFFICER': 
            officer.ministry = user.ministry or 'Ministry of Digital Economy' 
        else: 
            officer.ministry = 'Test Ministry' 
 
        # Set department for Reporting Officer 
        if user.role == 'REPORTING_OFFICER': 
            officer.department = user.department or 'Test Department' 
        else: 
            officer.department = 'Test Department' 
 
        db.session.add(officer) 
        created += 1 
        print(f'Created officer profile for {user.username}') 
 
    db.session.commit() 
    print(f'Created {created} officer profiles') 
