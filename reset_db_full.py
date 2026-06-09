import os 
import sqlite3 
from app import create_app, db 
from app.models.user import User 
from app.models.officer import Officer 
from app.models.performance_report import PerformanceReport 
from app.models.assessment import Assessment 
 
# Delete old database 
if os.path.exists('instance/appraisal.db'): 
    os.remove('instance/appraisal.db') 
    print('Removed old database') 
 
# Create new database with all tables 
app = create_app() 
with app.app_context(): 
    db.create_all() 
    print('Database created with all columns') 
 
    # Create admin user 
    admin = User(username='admin', email='admin@example.com', role='ADMIN', is_active=True) 
    admin.set_password('Admin123') 
    db.session.add(admin) 
 
    # Create other users 
    for username, email, role in [ 
        ('reporting_officer', 'ro@example.com', 'REPORTING_OFFICER'), 
        ('countersigning_officer', 'co@example.com', 'COUNTERSIGNING_OFFICER'), 
        ('hr_officer', 'hr@example.com', 'HR'), 
        ('john_doe', 'john@example.com', 'OFFICER'): 
        user = User(username=username, email=email, role=role, is_active=True) 
        user.set_password('password123') 
        db.session.add(user) 
    db.session.commit() 
    print('Users created') 
 
print('Reset complete!') 
