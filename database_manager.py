import sqlite3
import json

def init_db():
    conn = sqlite3.connect('x1_vault.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_name TEXT,
            grand_total REAL,
            audit_status TEXT,
            flags TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def generate_danger_report(data):
    """The 'Alarm'—creates a text file if something is wrong."""
    status = data.get("audit_report", {}).get("status")
    
    if status == "DISCREPANCY_FOUND":
        vendor = data.get("vendor_name", "Unknown")
        flags = data.get("audit_report", {}).get("flags", [])
        
        # Creates a file like CRITICAL_ALERT_Your_Company.txt
        filename = f"CRITICAL_ALERT_{vendor.replace(' ', '_')}.txt"
        
        with open(filename, "w") as f:
            f.write("--- X1 CRITICAL DISCREPANCY REPORT ---\n")
            f.write(f"VENDOR: {vendor}\n")
            f.write("\nISSUES DETECTED:\n")
            for flag in flags:
                f.write(f"{flag}\n")
            f.write("\nACTION REQUIRED: DO NOT PAY UNTIL VERIFIED.\n")
        print(f"[!] DANGER REPORT GENERATED: {filename}")

def save_audit_to_db(data):
    """Saves to the Vault AND triggers the Danger Report if needed."""
    conn = sqlite3.connect('x1_vault.db')
    cursor = conn.cursor()
    
    vendor = data.get("vendor_name", "Unknown")
    total = data.get("grand_total", 0.0)
    status = data.get("audit_report", {}).get("status", "UNKNOWN")
    flags = " | ".join(data.get("audit_report", {}).get("flags", []))
    
    cursor.execute('''
        INSERT INTO audits (vendor_name, grand_total, audit_status, flags)
        VALUES (?, ?, ?, ?)
    ''', (vendor, total, status, flags))
    
    conn.commit()
    conn.close()
    print(f"[✓] Audit saved to X1 Vault.")

    # THIS IS STEP 2: We call the reporter right after saving
    generate_danger_report(data)