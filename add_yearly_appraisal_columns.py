# add_yearly_appraisal_columns.py
import sqlite3

conn = sqlite3.connect('instance/appraisal.db')
cursor = conn.cursor()

# List of columns to add to yearly_appraisals table
columns_to_add = [
    "ALTER TABLE yearly_appraisals ADD COLUMN section_b_work_output FLOAT DEFAULT 0",
    "ALTER TABLE yearly_appraisals ADD COLUMN section_b_innovation FLOAT DEFAULT 0",
    "ALTER TABLE yearly_appraisals ADD COLUMN section_b_leadership FLOAT DEFAULT 0",
    "ALTER TABLE yearly_appraisals ADD COLUMN section_b_teamwork FLOAT DEFAULT 0",
    "ALTER TABLE yearly_appraisals ADD COLUMN section_b_communication FLOAT DEFAULT 0",
    "ALTER TABLE yearly_appraisals ADD COLUMN section_b_ethics FLOAT DEFAULT 0",
    "ALTER TABLE yearly_appraisals ADD COLUMN officer_comments TEXT",
    "ALTER TABLE yearly_appraisals ADD COLUMN countersigning_officer_id INTEGER",
    "ALTER TABLE yearly_appraisals ADD COLUMN total_score FLOAT DEFAULT 0",
    "ALTER TABLE yearly_appraisals ADD COLUMN rating VARCHAR(50) DEFAULT 'Not Rated'",
    "ALTER TABLE yearly_appraisals ADD COLUMN reporting_officer_id INTEGER",
    "ALTER TABLE yearly_appraisals ADD COLUMN created_at TIMESTAMP",
    "ALTER TABLE yearly_appraisals ADD COLUMN updated_at TIMESTAMP"
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