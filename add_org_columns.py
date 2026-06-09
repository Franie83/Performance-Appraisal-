import sqlite3 
 
conn = sqlite3.connect('instance/appraisal.db') 
cursor = conn.cursor() 
 
# Add mda column 
try: 
    cursor.execute('ALTER TABLE officers ADD COLUMN mda VARCHAR(200)') 
    print('Added mda column') 
except: 
    print('mda column already exists') 
 
# Add department column 
try: 
    cursor.execute('ALTER TABLE officers ADD COLUMN department VARCHAR(200)') 
    print('Added department column') 
except: 
    print('department column already exists') 
 
# Add unit column 
try: 
    cursor.execute('ALTER TABLE officers ADD COLUMN unit VARCHAR(200)') 
    print('Added unit column') 
except: 
    print('unit column already exists') 
 
conn.commit() 
conn.close() 
print('Organization fields added successfully!') 
