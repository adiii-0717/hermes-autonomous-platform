import json
import os
from datetime import datetime

DATA_FILE = "data/attendance_records.json"

def initialize_data():
    """Ensure the data file exists and is initialized."""
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)

def load_records():
    init_data()
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_records(records):
    with open(DATA_FILE, "w") as f:
        json.dump(records, f, indent=4)

def mark_attendance(roll_number):
    """Allows a student to mark attendance for the current date."""
    records = load_records()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Basic validation: check if roll number is valid (not empty)
    if not roll_number or len(roll_number) < 3:
        return False, "Invalid Roll Number!"

    if today in records:
        if roll_number in records[today]:
            return False, f"Attendance already marked for {roll_number} on {today}."
    else:
        records[today] = []
    
    records[today].append(roll_number)
    save_records(records)
    return True, f"Success! Attendance recorded for {roll_number} on {today}."

def generate_monthly_report(month_str):
    """
    Generates a report for a given month. 
    Month format expected: YYYY-MM (e.g., '2024-08')
    """
    records = load_records()
    # Filter records that match the prefix (Year and Month)
    monthly_data = {}
    for date, rolls in records.items():
        if date.startswith(month_str):
            monthly_data[date] = rolls
    
    if not monthly_data:
        return None, f"No records found for {month_str}."
    
    report = []
    for date, rolls in monthly_data.items():
        report.append(f"Date: {date} | Present: {', '.join(rolls)}")
    
    return "\n".join(report), None
