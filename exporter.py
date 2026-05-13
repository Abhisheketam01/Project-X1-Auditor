import sqlite3
import csv

def export_to_csv():
    conn = sqlite3.connect('x1_vault.db')
    cursor = conn.cursor()
    
    # Fetch everything from the vault
    cursor.execute("SELECT * FROM audits")
    rows = cursor.fetchall()
    
    # Define the column headers
    headers = [description[0] for description in cursor.description]
    
    with open('X1_Final_Audit_Report.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers) # Write headers first
        writer.writerows(rows)   # Write all database data
        
    conn.close()
    print("[✓] SUCCESS: Data exported to X1_Final_Audit_Report.csv")

if __name__ == "__main__":
    export_to_csv()