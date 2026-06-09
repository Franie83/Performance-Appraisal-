python -c "with open('complete_setup.py', 'w') as f: f.write('''import os
import sys

# Create app/extensions.py
extensions_content = '''from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page'
'''

# Create app/__init__.py
init_content = '''from flask import Flask, redirect, url_for
from app.extensions import db, login_manager, mail, migrate
from config import config

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    with app.app_context():
        db.create_all()
    
    from app.auth import auth_bp
    from app.reports import reports_bp
    from app.admin import admin_bp
    from app.officers import officers_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(officers_bp, url_prefix='/officers')
    
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    return app
'''

# Create app/models/user.py
user_content = '''from app.extensions import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role):
        return self.role == role or self.role == 'ADMIN'
    
    @property
    def officer_profile(self):
        from app.models.officer import Officer
        return Officer.query.filter_by(user_id=self.id).first()
    
    def __repr__(self):
        return f'<User {self.username}>'
'''

# Create app/models/officer.py
officer_content = '''from app.extensions import db
from datetime import datetime

class Officer(db.Model):
    __tablename__ = 'officers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    staff_no = db.Column(db.String(50), unique=True)
    surname = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    other_names = db.Column(db.String(200))
    title = db.Column(db.String(20))
    ministry = db.Column(db.String(200))
    department = db.Column(db.String(200))
    division = db.Column(db.String(200))
    branch = db.Column(db.String(200))
    section = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='officer_record', uselist=False)
    
    @property
    def full_name(self):
        return f"{self.surname} {self.first_name} {self.other_names or ''}".strip()
    
    def __repr__(self):
        return f'<Officer {self.staff_no}: {self.full_name}>'
'''

# Create app/models/__init__.py
models_init = '''from app.models.user import User
from app.models.officer import Officer

__all__ = ['User', 'Officer']
'''

# Write all files
os.makedirs('app/extensions', exist_ok=True)
os.makedirs('app/models', exist_ok=True)
os.makedirs('app/auth', exist_ok=True)
os.makedirs('app/reports', exist_ok=True)
os.makedirs('app/admin', exist_ok=True)
os.makedirs('app/officers', exist_ok=True)

with open('app/extensions.py', 'w') as f:
    f.write(extensions_content)
print('Created app/extensions.py')

with open('app/__init__.py', 'w') as f:
    f.write(init_content)
print('Created app/__init__.py')

with open('app/models/user.py', 'w') as f:
    f.write(user_content)
print('Created app/models/user.py')

with open('app/models/officer.py', 'w') as f:
    f.write(officer_content)
print('Created app/models/officer.py')

with open('app/models/__init__.py', 'w') as f:
    f.write(models_init)
print('Created app/models/__init__.py')

print('\\nAll files created successfully!')
''')"