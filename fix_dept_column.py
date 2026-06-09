import sqlite3 
 
conn = sqlite3.connect('instance/appraisal.db') 
cursor = conn.cursor() 
 
try: 
    cursor.execute('ALTER TABLE officers ADD COLUMN dept VARCHAR(200)') 
    print('Added dept column') 
except Exception as e: 
    print(f'dept column might already exist: {e}') 
 
conn.commit() 
conn.close() 
print('Done!') 
