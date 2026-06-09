import os 
import sys 
sys.path.insert(0, os.getcwd()) 
 
from app import create_app, db 
from app.models.user import User 
from app.models.officer import Officer 
from app.models.performance_report import PerformanceReport 
from app.models.assessment import Assessment 
 
# Delete old database 
db_path = 'instance/appraisal.db' 
if os.path.exists(db_path): 
    os.remove(db_path) 
    print('Removed old database') 
 
# Create new database 
app = create_app() 
with app.app_context(): 
    db.create_all() 
    print('Database created with all tables') 
 
    # Create admin user 
    admin = User(username='admin', email='admin@example.com', role='ADMIN', is_active=True) 
    admin.set_password('Admin123') 
    db.session.add(admin) 
    print('Added admin') 
 
    # Create reporting officer 
    ro = User(username='reporting_officer', email='ro@example.com', role='REPORTING_OFFICER', is_active=True) 
    ro.set_password('password123') 
    db.session.add(ro) 
    print('Added reporting_officer') 
 
    # Create countersigning officer 
    co = User(username='countersigning_officer', email='co@example.com', role='COUNTERSIGNING_OFFICER', is_active=True) 
    co.set_password('password123') 
    db.session.add(co) 
    print('Added countersigning_officer') 
 
    # Create HR officer 
    hr = User(username='hr_officer', email='hr@example.com', role='HR', is_active=True) 
    hr.set_password('password123') 
    db.session.add(hr) 
    print('Added hr_officer') 
 
    # Create regular officer 
    officer = User(username='john_doe', email='john@example.com', role='OFFICER', is_active=True) 
    officer.set_password('password123') 
    db.session.add(officer) 
    print('Added john_doe') 
 
    db.session.commit() 
    print('All users created successfully!') 
 
print('='*50) 
print('Database reset complete!') 
print('='*50) 
