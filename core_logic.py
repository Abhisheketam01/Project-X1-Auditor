import os
import json
from google import genai
from dotenv import load_dotenv

# --- GLOBAL TOGGLE ---
# True  = Mock Mode  (no API calls, no quota usage)
# False = Real Mode  (calls Gemini API)
SIMULATION_MODE = True

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def validate_audit_logic(data):
    """
    Performs internal arithmetic checks to find math errors in invoice.
    """
    audit_report = {"status": "SUCCESS", "flags": []}
    calculated_grand_total = 0.0

    print("\n--- X1 INTERNAL AUDIT SEQUENCE ---")

    items = data.get('items', [])
    for item in items:
        qty          = item.get('qty', 0)
        rate         = item.get('rate', 0.0)
        reported_total = item.get('total', 0.0)

        expected_total = qty * rate
        calculated_grand_total += reported_total

        if abs(expected_total - reported_total) > 0.01:
            flag = f"[!] MATH ERROR: '{item.get('desc', 'Unknown')}' | Expected {expected_total:.2f}, but found {reported_total:.2f}"
            print(flag)
            audit_report["flags"].append(flag)
            audit_report["status"] = "DISCREPANCY_FOUND"

    reported_grand_total = data.get('grand_total', 0.0)
    if abs(calculated_grand_total - reported_grand_total) > 0.01:
        flag = f"[!] TOTAL MISMATCH: Items sum to {calculated_grand_total:.2f}, but Grand Total says {reported_grand_total:.2f}"
        print(flag)
        audit_report["flags"].append(flag)
        audit_report["status"] = "DISCREPANCY_FOUND"

    if audit_report["status"] == "SUCCESS":
        print("[✓] Integrity Verified. No arithmetic errors found.")

    return audit_report


def run_simulation(image_path):
    """
    Returns mock invoice data — no API call, no quota usage.
    """
    print(f"\n[X1_SIMULATOR] (MOCK MODE) Scanning: {image_path}...")

    mock_data = {
        "vendor_name": "Your Company Inc.",
        "date": "10-02-2023",
        "items": [
            {"desc": "Replacement of spark plugs",     "qty": 1, "rate": 40.0,  "total": 75.0},
            {"desc": "Brake pad replacement (front)",  "qty": 2, "rate": 40.0,  "total": 80.0},
            {"desc": "Wheel alignment",                "qty": 4, "rate": 17.5,  "total": 70.0}
        ],
        "grand_total": 190.0
    }

    audit_results = validate_audit_logic(mock_data)
    mock_data["audit_report"] = audit_results
    return json.dumps(mock_data, indent=4)


def run_real_inference(image_path):
    """
    Calls the real Gemini API to extract invoice data from image.
    """
    print(f"\n[X1_CORE] (API MODE) Calling Gemini Engine for: {image_path}...")

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            {
                "parts": [
                    {"text": "Extract invoice data as JSON with fields: vendor_name, date, items (desc, qty, rate, total), grand_total."},
                    {"inline_data": {"mime_type": "image/jpeg", "data": image_bytes}}
                ]
            }
        ]
    )

    raw = response.text.strip().removeprefix("```json").removesuffix("```").strip()
    data = json.loads(raw)

    audit_results = validate_audit_logic(data)
    data["audit_report"] = audit_results
    return json.dumps(data, indent=4)


def extract_invoice_data(image_path):
    """
    Master function — routes to simulation or real API based on toggle.
    """
    if SIMULATION_MODE:
        return run_simulation(image_path)
    else:
        return run_real_inference(image_path)