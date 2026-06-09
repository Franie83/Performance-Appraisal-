from app import create_app, db 
from app.models.user import User 
 
def create_admin(): 
    app = create_app() 
    with app.app_context(): 
        admin = User.query.filter_by(username='admin').first() 
        if admin: 
            print(f'Admin already exists! Username: {admin.username}') 
        else: 
            admin = User(username='admin', email='admin@example.com', role='ADMIN') 
            admin.set_password('Admin123') 
            db.session.add(admin) 
            db.session.commit() 
            print('Admin user created!') 
            print('Username: admin') 
            print('Password: Admin123') 
 
if __name__ == '__main__': 
    create_admin() 
