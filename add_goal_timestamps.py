import sqlite3

conn = sqlite3.connect('instance/appraisal.db')
cursor = conn.cursor()

columns_to_add = [
    "ALTER TABLE quarterly_goals ADD COLUMN created_at TIMESTAMP",
    "ALTER TABLE quarterly_goals ADD COLUMN updated_at TIMESTAMP"
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