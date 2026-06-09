import sqlite3

conn = sqlite3.connect('instance/appraisal.db')
cursor = conn.cursor()

# Create audit_logs table
cursor.execute('''
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    username VARCHAR(100) NOT NULL,
    user_role VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    entity_name VARCHAR(200),
    old_value TEXT,
    new_value TEXT,
    changes TEXT,
    ip_address VARCHAR(50),
    user_agent VARCHAR(300),
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

print("✅ audit_logs table created successfully!")

conn.commit()
conn.close()