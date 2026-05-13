import os
import json
from core_logic import extract_invoice_data
from database_manager import init_db, save_audit_to_db

def run_bulk_audit(input_folder):
    # --- ADD THIS CLEANUP BLOCK HERE ---
    print("[LOG] Clearing old alerts...")
    for f in os.listdir("."):
        if f.startswith("CRITICAL_ALERT_") and f.endswith(".txt"):
            os.remove(f)

            
    init_db()
    
    # Get all images in the folder
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(valid_extensions)]
    
    if not files:
        print(f"[!] No images found in {input_folder}")
        return

    print(f"--- X1 BULK EXTRACTION: {len(files)} FILES FOUND ---")

    for filename in files:
        file_path = os.path.join(input_folder, filename)
        
        # 1. Process the file
        result_json_str = extract_invoice_data(file_path)
        result_data = json.loads(result_json_str)
        
        # 2. Save to Vault
        save_audit_to_db(result_data)
        
        print(f"[✓] Completed: {filename}")
        print("-" * 30)

    print("\n--- ALL TASKS COMPLETE. CHECK INSPECTOR.PY FOR RESULTS ---")

if __name__ == "__main__":
    INPUT_DIR = "data/input"
    run_bulk_audit(INPUT_DIR)