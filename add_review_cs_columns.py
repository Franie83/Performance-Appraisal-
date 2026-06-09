# add_review_cs_columns.py
import sqlite3

conn = sqlite3.connect('instance/appraisal.db')
cursor = conn.cursor()

columns_to_add = [
    "ALTER TABLE quarterly_goals ADD COLUMN cs_review_approved BOOLEAN DEFAULT 0",
    "ALTER TABLE quarterly_goals ADD COLUMN cs_review_approved_at DATETIME",
    "ALTER TABLE quarterly_goals ADD COLUMN cs_review_approved_by INTEGER",
    "ALTER TABLE quarterly_goals ADD COLUMN cs_review_comments TEXT"
]

for sql in columns_to_add:
    try:
        cursor.execute(sql)
        print(f"✅ Added column: {sql.split('ADD COLUMN')[1].strip()}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"⚠️ Column already exists")
        else:
            print(f"❌ Error: {e}")

conn.commit()
conn.close()
print("\n✅ Database update complete!")