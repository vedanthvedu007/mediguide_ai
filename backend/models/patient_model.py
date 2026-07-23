"""
models/patient_model.py — Patient Symptom History Model
========================================================
Handles all read/write operations for the `patients` collection.

Schema (MongoDB document):
  {
    "_id":          ObjectId,
    "email":        str,
    "symptoms":     str,
    "risk":         int  (0–100),
    "triage_level": str  ("HOME_CARE" | "CLINIC_VISIT" | "EMERGENCY"),
    "date":         str  ("YYYY-MM-DD"),
    "timestamp":    datetime
  }
"""

from datetime import datetime, timezone, timedelta
from db.mongo import get_db, is_connected


def save_check(email: str, symptoms: str, risk: int, triage_level: str) -> None:
    """Insert a new symptom check record for this patient."""
    if not email or not is_connected():
        return
    db = get_db()
    db["patients"].insert_one({
        "email":        email.strip().lower(),
        "symptoms":     symptoms,
        "risk":         risk,
        "triage_level": triage_level,
        "date":         datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "timestamp":    datetime.now(timezone.utc),
    })


def get_history(email: str, limit: int = 20) -> list[dict]:
    """
    Return the most recent `limit` symptom checks for this patient,
    sorted newest-first. Converts ObjectId → string for JSON safety.
    """
    if not email or not is_connected():
        return []
    db = get_db()
    cursor = (
        db["patients"]
        .find({"email": email.strip().lower()}, {"_id": 0})
        .sort("timestamp", -1)
        .limit(limit)
    )
    return list(cursor)


def check_recurring(email: str, symptoms: str) -> bool:
    """
    Return True if the same symptom string was recorded for this patient
    within the past 2 days (indicating a recurring condition).
    """
    if not email or not is_connected():
        return False
    db = get_db()
    two_days_ago = datetime.now(timezone.utc) - timedelta(days=2)
    count = db["patients"].count_documents({
        "email":    email.strip().lower(),
        "symptoms": symptoms,
        "timestamp": {"$gte": two_days_ago},
    })
    return count > 0


def get_patient_name(email: str) -> str:
    """Return the patient's registered name, or the email as fallback."""
    if not email or not is_connected():
        return ""
    db = get_db()
    user = db["users"].find_one(
        {"email": email.strip().lower()},
        {"name": 1, "_id": 0}
    )
    return user["name"] if user else email
