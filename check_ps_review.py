# check_ps_review.py
from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal

app = create_app()
with app.app_context():
    print("=" * 60)
    print("CHECKING FOR PS_REVIEW APPRAISALS")
    print("=" * 60)
    
    # Find appraisals that need countersigning officer review
    ps_review = YearlyAppraisal.query.filter(
        YearlyAppraisal.status == 'PS_REVIEW'
    ).all()
    
    if ps_review:
        print(f"\n✅ Found {len(ps_review)} appraisal(s) in PS_REVIEW status:")
        for a in ps_review:
            print(f"\n  Appraisal ID: {a.id}")
            print(f"  Officer: {a.user.username}")
            print(f"  Year: {a.appraisal_year}")
            print(f"  Officer Agrees: {a.officer_agrees}")
            print(f"  🔗 Direct URL: http://localhost:5000/quarterly/ps-review/{a.id}")
    else:
        print("\n❌ No appraisals in PS_REVIEW status found")
        
        # Check what statuses exist
        print("\nAll appraisals and their statuses:")
        all_appraisals = YearlyAppraisal.query.all()
        for a in all_appraisals:
            print(f"  ID {a.id}: {a.user.username} - {a.appraisal_year} - Status: {a.status}")
        
        # Check if any appraisals have officer_agrees=True but not in PS_REVIEW
        officer_accepted = YearlyAppraisal.query.filter(
            YearlyAppraisal.officer_agrees == True,
            YearlyAppraisal.status != 'FINALIZED'
        ).all()
        
        if officer_accepted:
            print(f"\n⚠️ Found {len(officer_accepted)} appraisal(s) where officer agreed but status not updated:")
            for a in officer_accepted:
                print(f"  ID {a.id}: Status is {a.status} - Should be PS_REVIEW or FINALIZED")