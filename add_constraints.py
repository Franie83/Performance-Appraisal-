import sqlite3 
 
conn = sqlite3.connect('instance/appraisal.db') 
cursor = conn.cursor() 
 
# Add department field to users table if not exists 
try: 
    cursor.execute('ALTER TABLE users ADD COLUMN department VARCHAR(200)') 
    print('Added department column to users') 
except: 
    print('department column already exists') 
 
# Add ministry field to users table if not exists 
try: 
    cursor.execute('ALTER TABLE users ADD COLUMN ministry VARCHAR(200)') 
    print('Added ministry column to users') 
except: 
    print('ministry column already exists') 
 
conn.commit() 
conn.close() 
print('Database updated successfully!') 
