# check_model.py
from app import create_app, db
from app.models.quarterly_plan import YearlyAppraisal

app = create_app()
with app.app_context():
    # Get a sample appraisal
    appraisal = YearlyAppraisal.query.first()
    
    if appraisal:
        print("YearlyAppraisal Model Attributes:")
        print("=" * 50)
        for column in appraisal.__table__.columns:
            print(f"  - {column.name}")
        print("=" * 50)
    else:
        print("No appraisal found")
