import sqlite3

conn = sqlite3.connect('instance/appraisal.db')
cursor = conn.cursor()

# Find duplicate staff numbers
cursor.execute("""
    SELECT staff_no, COUNT(*) as count 
    FROM officers 
    WHERE staff_no IS NOT NULL 
    GROUP BY staff_no 
    HAVING count > 1
""")
duplicates = cursor.fetchall()

if duplicates:
    print("Found duplicate staff numbers:")
    for staff_no, count in duplicates:
        print(f"  {staff_no}: {count} occurrences")
        
        # Get all officers with this staff number
        cursor.execute("SELECT id, staff_no, surname, first_name FROM officers WHERE staff_no = ?", (staff_no,))
        officers = cursor.fetchall()
        
        for i, officer in enumerate(officers):
            officer_id, old_staff_no, surname, first_name = officer
            if i == 0:
                print(f"    Keeping: ID {officer_id} - {surname} {first_name}")
            else:
                new_staff_no = f"{old_staff_no}_{officer_id}"
                cursor.execute("UPDATE officers SET staff_no = ? WHERE id = ?", (new_staff_no, officer_id))
                print(f"    Updated: ID {officer_id} to {new_staff_no}")
    
    conn.commit()
    print("\nDuplicate staff numbers fixed!")
else:
    print("No duplicate staff numbers found.")

# Show current officers
print("\nCurrent officers:")
cursor.execute("SELECT id, staff_no, surname, first_name FROM officers")
officers = cursor.fetchall()
for officer in officers:
    print(f"  ID: {officer[0]}, Staff No: {officer[1]}, Name: {officer[2]} {officer[3]}")

conn.close()
print("\nDone!")