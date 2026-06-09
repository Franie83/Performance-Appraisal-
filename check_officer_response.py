# check_officer_response.py
from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal

app = create_app()
with app.app_context():
    appraisal = YearlyAppraisal.query.filter_by(id=3).first()
    
    if appraisal:
        print("=" * 50)
        print("Officer Response Check")
        print("=" * 50)
        print(f"Status: {appraisal.status}")
        print(f"Officer Agrees: {appraisal.officer_agrees}")
        print(f"Officer Response At: {appraisal.officer_response_at}")
        
        # Check if officer_agrees is set
        if appraisal.officer_agrees is True:
            print("\n✅ Officer ACCEPTED the assessment")
            print("   Appraisal should be finalized or sent to PS")
        elif appraisal.officer_agrees is False:
            print("\n⚠️ Officer DISAGREED with the assessment")
            print("   Appraisal returned to Reporting Officer")
        else:
            print("\n⚠️ Officer has NOT responded yet")
    else:
        print("Appraisal not found")