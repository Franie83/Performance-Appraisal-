from app import create_app, db 
from app.models.user import User 
 
app = create_app() 
with app.app_context(): 
    # Update reporting officer with department 
    ro = User.query.filter_by(username='reporting_officer').first() 
    if ro: 
        ro.department = 'Digital Economy and Innovation' 
        print(f'Updated {ro.username}: department={ro.department}') 
    else: 
        print('reporting_officer not found') 
 
    # Update countersigning officer with ministry 
    co = User.query.filter_by(username='countersigning_officer').first() 
    if co: 
        co.ministry = 'Ministry of Digital Economy' 
        print(f'Updated {co.username}: ministry={co.ministry}') 
    else: 
        print('countersigning_officer not found') 
 
    db.session.commit() 
    print('Done!') 
