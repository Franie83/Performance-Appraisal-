from app import create_app, db
from app.models import User

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ Database tables created.")
        
        # Optional: create admin user if missing
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@example.com', role='ADMIN')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created.")

if __name__ == "__main__":
    init_db()