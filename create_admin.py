from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f'Admin already exists: {admin.username}')
    else:
        admin = User(username='admin', email='admin@example.com', role='ADMIN')
        admin.set_password('Admin123')
        db.session.add(admin)
        db.session.commit()
        print('Admin created! Username: admin, Password: Admin123')