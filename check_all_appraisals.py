# check_all_appraisals.py
from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal
from app.models.user import User

app = create_app()
with app.app_context():
    print("=" * 60)
    print("ALL APPRAISALS DETAIL")
    print("=" * 60)
    
    # Get john_doe user
    john = User.query.filter_by(username='john_doe').first()
    
    if john:
        print(f"\nOfficer: {john.username} (ID: {john.id})")
        
        # Get all appraisals for john_doe
        appraisals = YearlyAppraisal.query.filter_by(user_id=john.id).order_by(YearlyAppraisal.appraisal_year.desc()).all()
        
        if appraisals:
            print(f"\nFound {len(appraisals)} appraisal(s):")
            for a in appraisals:
                print(f"\n  Appraisal ID: {a.id}")
                print(f"  Year: {a.appraisal_year}")
                print(f"  Status: {a.status}")
                print(f"  Section B Total: {a.section_b_total}")
                print(f"  Officer Agrees: {a.officer_agrees}")
                print(f"  Finalized At: {a.finalized_at}")
        else:
            print("\n❌ No appraisals found for john_doe")
    else:
        print("❌ User john_doe not found")