import sqlite3

def view_all_audits():
    conn = sqlite3.connect('x1_vault.db')
    cursor = conn.cursor()
    
    print("\n--- X1 VAULT: HISTORICAL RECORDS ---")
    cursor.execute("SELECT id, vendor_name, grand_total, audit_status, timestamp FROM audits")
    records = cursor.fetchall()
    
    if not records:
        print("Vault is empty.")
    else:
        for r in records:
            print(f"ID: {r[0]} | Vendor: {r[1]} | Total: {r[2]} | Status: {r[3]} | Date: {r[4]}")
            
    conn.close()

def get_stats():
    conn = sqlite3.connect('x1_vault.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM audits WHERE audit_status = 'DISCREPANCY_FOUND'")
    discrepancies = cursor.fetchone()[0]
    
    print(f"\n--- X1 INTELLIGENCE REPORT ---")
    print(f"Total Issues Flagged to Date: {discrepancies}")
    conn.close()

if __name__ == "__main__":
    view_all_audits()
    get_stats()