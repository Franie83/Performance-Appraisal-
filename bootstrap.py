import sys 
import os 
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))) 
 
from app import create_app, db 
from app.models.user import User 
from app.models.officer import Officer 
from app.models.performance_report import PerformanceReport 
from app.models.assessment import Assessment 
from app.models.countersignature import Countersignature 
from app.models.officer_declaration import OfficerDeclaration 
 
def init_db(): 
    print('Creating Flask app...') 
    app = create_app() 
    print('App created successfully!') 
 
    with app.app_context(): 
        print('Creating database tables...') 
        db.create_all() 
        print('Tables created successfully!') 
 
        print('Checking for admin user...') 
        admin = User.query.filter_by(username='admin').first() 
        if admin: 
            print(f'Admin user already exists: {admin.username}') 
        else: 
            admin = User( 
                username='admin', 
                email='admin@example.com', 
                role='ADMIN', 
                is_active=True 
            ) 
            admin.set_password('Admin123') 
            db.session.add(admin) 
            db.session.commit() 
            print('Admin user created successfully!') 
            print('Username: admin') 
            print('Password: Admin123') 
 
        users = User.query.all() 
        print(f'\nTotal users in database: {len(users)}') 
        for u in users: 
            print(f'  - {u.username} ({u.role})') 
 
    return app 
 
if __name__ == '__main__': 
    app = init_db() 
    print('\n' + '='*50) 
    print('Database initialization complete!') 
    print('='*50) 
    print('\nTo start the server, run: python run.py') 
