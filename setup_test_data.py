# setup_test_data.py
from app import create_app, db
from app.models.user import User
from app.models.quarterly_plan import YearlyAppraisal, QuarterlyGoal
from datetime import datetime

app = create_app()
with app.app_context():
    print("=" * 60)
    print("SETTING UP TEST DATA FOR MULTIPLE YEARS")
    print("=" * 60)
    
    # Delete all existing appraisals
    deleted = YearlyAppraisal.query.delete()
    print(f"✅ Deleted {deleted} existing appraisals")
    
    # Delete existing quarterly goals
    deleted_goals = QuarterlyGoal.query.delete()
    print(f"✅ Deleted {deleted_goals} existing quarterly goals")
    
    db.session.commit()
    
    # Get users
    john = User.query.filter_by(username='john_doe').first()
    ro = User.query.filter_by(role='REPORTING_OFFICER').first()
    ps = User.query.filter_by(role='PERMANENT_SECRETARY').first()
    
    if not ps:
        # Create a PERMANENT_SECRETARY if doesn't exist
        ps = User(
            username='permanent_secretary',
            email='ps@example.com',
            role='PERMANENT_SECRETARY',
            is_active=True
        )
        ps.set_password('password123')
        db.session.add(ps)
        db.session.commit()
        print("✅ Created PERMANENT_SECRETARY user")
    
    print(f"\nUsers found:")
    print(f"  - Officer: {john.username} (ID: {john.id})")
    print(f"  - Reporting Officer: {ro.username} (ID: {ro.id})")
    print(f"  - Permanent Secretary: {ps.username} (ID: {ps.id})")
    
    # Create appraisals for different years
    years = [2023, 2024, 2025, 2026]
    
    for year in years:
        appraisal = YearlyAppraisal(
            user_id=john.id,
            appraisal_year=year,
            status='DRAFT',
            reporting_officer_id=ro.id
        )
        db.session.add(appraisal)
        print(f"✅ Created {year} appraisal (ID: will be assigned)")
    
    db.session.commit()
    
    # Get the created appraisals
    appraisals = YearlyAppraisal.query.filter_by(user_id=john.id).order_by(YearlyAppraisal.appraisal_year).all()
    
    print("\n" + "=" * 60)
    print("CREATED APPRAISALS:")
    print("=" * 60)
    for a in appraisals:
        print(f"  - {a.appraisal_year}: ID={a.id}, Status={a.status}")
    
    print("\n" + "=" * 60)
    print("TO TEST THE WORKFLOW:")
    print("=" * 60)
    print("1. Login as john_doe (password: password123)")
    print("2. Go to Quarterly Dashboard → Yearly Appraisal")
    print("3. Select a year (start with 2026)")
    print("4. Fill out Section B scores and submit")
    print("5. Login as reporting_officer (password: password123)")
    print("6. Assess and approve the appraisal")
    print("7. Login as john_doe again and respond")
    print("8. Login as permanent_secretary (password: password123) and finalize")
    print("9. Download PDF")