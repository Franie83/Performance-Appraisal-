import sqlite3 
 
conn = sqlite3.connect('instance/appraisal.db') 
cursor = conn.cursor() 
 
columns_to_add = [ 
    ('staff_no', 'VARCHAR(50)'), 
    ('surname', 'VARCHAR(100)'), 
    ('first_name', 'VARCHAR(100)'), 
    ('other_names', 'VARCHAR(200)'), 
    ('title', 'VARCHAR(20)'), 
    ('date_of_birth', 'DATE'), 
    ('date_first_appointment', 'DATE'), 
    ('post_appointed', 'VARCHAR(200)'), 
    ('present_post', 'VARCHAR(200)'), 
    ('salary_grade', 'VARCHAR(50)'), 
    ('ministry', 'VARCHAR(200)'), 
    ('department', 'VARCHAR(200)'), 
    ('division', 'VARCHAR(200)'), 
    ('branch', 'VARCHAR(200)'), 
    ('section', 'VARCHAR(200)') 
] 
 
for col_name, col_type in columns_to_add: 
    try: 
        cursor.execute(f'ALTER TABLE users ADD COLUMN {col_name} {col_type}') 
        print(f'Added column: {col_name}') 
    except Exception as e: 
        print(f'Column {col_name} already exists or error: {e}') 
 
conn.commit() 
conn.close() 
print('Database updated successfully!') 
