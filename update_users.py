from app import create_app, db 
from app.models.user import User 
 
app = create_app() 
with app.app_context(): 
    users = User.query.all() 
    for user in users: 
        if not user.surname: 
            user.surname = user.username.capitalize() 
        if not user.first_name: 
            user.first_name = user.role.capitalize() 
        if not user.staff_no: 
            user.staff_no = f'STAFF{user.id:03d}' 
        if not user.ministry: 
            user.ministry = 'Ministry of Digital Economy' if user.role == 'COUNTERSIGNING_OFFICER' else 'Test Ministry' 
        if not user.department: 
            user.department = 'Test Department' 
        print(f'Updated user: {user.username}') 
    db.session.commit() 
    print('All users updated successfully!') 
