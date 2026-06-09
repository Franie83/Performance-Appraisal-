import sqlite3

conn = sqlite3.connect('instance/appraisal.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE audit_logs ADD COLUMN module VARCHAR(50)")
    print("✅ Added module column to audit_logs table")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("⚠️ Module column already exists")
    else:
        print(f"❌ Error: {e}")

conn.commit()
conn.close()