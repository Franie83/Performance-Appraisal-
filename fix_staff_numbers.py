from app import create_app, db
from app.models.officer import Officer

app = create_app()

with app.app_context():
    from sqlalchemy import func
    
    # Find duplicate staff numbers
    duplicates = db.session.query(
        Officer.staff_no, 
        func.count(Officer.id).label('count')
    ).group_by(Officer.staff_no).having(func.count(Officer.id) > 1).all()
    
    if duplicates:
        print("Found duplicate staff numbers:")
        for staff_no, count in duplicates:
            print(f"  {staff_no}: {count} occurrences")
            
            officers = Officer.query.filter_by(staff_no=staff_no).all()
            for i, officer in enumerate(officers):
                if i == 0:
                    print(f"    Keeping: ID {officer.id} - {officer.full_name}")
                else:
                    new_staff_no = f"{staff_no}_{officer.id}"
                    officer.staff_no = new_staff_no
                    print(f"    Updated: ID {officer.id} to {new_staff_no}")
        
        db.session.commit()
        print("\nDuplicate staff numbers fixed!")
    else:
        print("No duplicate staff numbers found.")
    
    # Show current officers
    print("\nCurrent officers:")
    officers = Officer.query.all()
    for officer in officers:
        print(f"  ID: {officer.id}, Staff No: {officer.staff_no}, Name: {officer.full_name}")