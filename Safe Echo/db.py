import json
import os
from datetime import datetime

DB_FILE = "cloud_db.json"

def init_db():
    """Initialize the JSON database if it doesn't exist."""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump([], f)

def log_alert(alert_type, risk_level, details, status="Blocked"):
    """Log a new alert to the database."""
    init_db()
    
    new_alert = {
        "Time": datetime.now().strftime("%I:%M %p"),
        "Type": alert_type,
        "Risk": risk_level,
        "Status": status,
        "Details": details,
        "Timestamp": datetime.now().isoformat()
    }
    
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
        
        # Prepend new alert (newest first)
        data.insert(0, new_alert)
        
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=4)
            
        return True
    except Exception as e:
        print(f"Error logging alert: {e}")
        return False

def get_alerts():
    """Fetch all alerts from the database."""
    init_db()
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return []
