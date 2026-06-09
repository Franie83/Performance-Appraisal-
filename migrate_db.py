import sqlite3 
 
conn = sqlite3.connect('instance/appraisal.db') 
cursor = conn.cursor() 
 
# Add user_id column to performance_reports 
try: 
    cursor.execute('ALTER TABLE performance_reports ADD COLUMN user_id INTEGER') 
    print('Added user_id column') 
except Exception as e: 
    print(f'user_id column already exists or error: {e}') 
 
# Copy data from officer_id to user_id 
try: 
    cursor.execute('UPDATE performance_reports SET user_id = officer_id WHERE user_id IS NULL AND officer_id IS NOT NULL') 
    print('Copied officer_id to user_id') 
except Exception as e: 
    print(f'Error copying data: {e}') 
 
conn.commit() 
conn.close() 
print('Database migration completed!') 
