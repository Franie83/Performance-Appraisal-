from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    cs = User.query.filter_by(role='COUNTERSIGNING_OFFICER').first()
    if cs:
        print(f'Countersigning Officer exists: {cs.username}')
        print(f'ID: {cs.id}')
        print(f'Email: {cs.email}')
        print(f'Is Active: {cs.is_active}')
    else:
        print('No Countersigning Officer found!')
        print('Creating one...')
        
        # Create Countersigning Officer
        cs = User(
            username='countersigning_officer',
            email='countersign@example.com',
            role='COUNTERSIGNING_OFFICER',
            is_active=True,
            surname='Countersigning',
            first_name='Officer'
        )
        cs.set_password('password123')
        db.session.add(cs)
        db.session.commit()
        print(f'✅ Countersigning Officer created: countersigning_officer / password123')