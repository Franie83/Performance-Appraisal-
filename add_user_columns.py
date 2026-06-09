import sqlite3 
 
conn = sqlite3.connect('instance/appraisal.db') 
cursor = conn.cursor() 
 
# Add department column 
try: 
    cursor.execute('ALTER TABLE users ADD COLUMN department VARCHAR(200)') 
    print('Added department column') 
except Exception as e: 
    print('department already exists or error:', e) 
 
# Add ministry column 
try: 
    cursor.execute('ALTER TABLE users ADD COLUMN ministry VARCHAR(200)') 
    print('Added ministry column') 
except Exception as e: 
    print('ministry already exists or error:', e) 
 
conn.commit() 
conn.close() 
print('Database updated successfully!') 
