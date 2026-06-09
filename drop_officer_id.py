import sqlite3 
 
conn = sqlite3.connect('instance/appraisal.db') 
cursor = conn.cursor() 
 
# SQLite doesn't support DROP COLUMN directly, so we need to recreate the table 
try: 
    # Check if officer_id column exists 
    cursor.execute("PRAGMA table_info(performance_reports)") 
    columns = cursor.fetchall() 
    has_officer_id = any(col[1] == 'officer_id' for col in columns) 
 
    if has_officer_id: 
        # Create new table without officer_id 
        cursor.execute(''' 
            CREATE TABLE performance_reports_new AS 
            SELECT id, user_id, report_year, period_from, period_to, 
            sick_leave_days, sick_leave_details, ncl_days, ncl_details, 
            annual_leave_days, casual_leave_days, division_targets, appraiser_targets, 
            estimated_salary_cost, estimated_overhead_cost, estimated_capital_cost, 
            agreed_completion_time, quantity_conform_standard, quality_conform_standard, 
            main_duties, joint_discussion_with_supervisor, properly_equipped, 
            constraints_difficulties, difficulties_encountered, supervisor_assistance_methods, 
            periodic_review_frequency, performance_measured_up, solution_admonition, 
            final_evaluation_done, ad_hoc_duties, ad_hoc_duties_affected, 
            ad_hoc_brought_to_supervisor, schedule_duty_from, schedule_duty_to, 
            supervisor1_name, supervisor1_from, supervisor1_to, 
            supervisor2_name, supervisor2_from, supervisor2_to, 
            supervisor3_name, supervisor3_from, supervisor3_to, 
            date_submitted_to_reporting, status, created_at, updated_at, 
            submitted_at, qr_code, verification_code, 
            target_reporting_officer_id, target_countersigning_officer_id, 
            reporting_approved_at, countersigning_approved_at, 
            reporting_approved_by, countersigning_approved_by, 
            reporting_comments, countersigning_comments, final_status, rejection_reason 
            FROM performance_reports 
        ''') 
        print('Created new table without officer_id') 
 
        # Drop old table and rename new one 
        cursor.execute('DROP TABLE performance_reports') 
        cursor.execute('ALTER TABLE performance_reports_new RENAME TO performance_reports') 
        print('Dropped officer_id column successfully') 
    else: 
        print('officer_id column does not exist') 
except Exception as e: 
    print(f'Error: {e}') 
 
conn.commit() 
conn.close() 
print('Migration complete!') 
