"""
models/alert_model.py — Blood Bank Alert Model
===============================================
Handles all read/write operations for the `blood_bank_alerts` collection.

Schema (MongoDB document):
  {
    "_id":           ObjectId,
    "patient_email": str,
    "patient_name":  str,
    "symptoms":      str,
    "risk_score":    int,
    "triage_level":  str,
    "alert_time":    str  ("YYYY-MM-DD HH:MM:SS"),
    "alert_sent":    bool,
    "timestamp":     datetime
  }
"""

from datetime import datetime, timezone
from db.mongo import get_db, is_connected


def save_alert(
    patient_email: str,
    patient_name: str,
    symptoms: str,
    risk_score: int,
    triage_level: str,
) -> dict:
    """
    Insert a blood bank alert record and return info dict
    (used in the /predict API response).
    """
    alert_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    if not is_connected():
        import config
        return {
            "alert_triggered":   True,
            "alert_time":        alert_time,
            "blood_bank_contact": config.BLOOD_BANK_EMAIL,
            "blood_bank_phone":  config.BLOOD_BANK_PHONE,
            "message": (
                f"🚨 Blood bank alerted at {config.BLOOD_BANK_EMAIL} "
                "— Emergency team notified! (DB offline — alert not persisted)"
            ),
        }

    db = get_db()

    db["blood_bank_alerts"].insert_one({
        "patient_email": patient_email,
        "patient_name":  patient_name,
        "symptoms":      symptoms,
        "risk_score":    risk_score,
        "triage_level":  triage_level,
        "alert_time":    alert_time,
        "alert_sent":    True,
        "timestamp":     datetime.now(timezone.utc),
    })

    import config  # lazy import to avoid circular dependency
    return {
        "alert_triggered":   True,
        "alert_time":        alert_time,
        "blood_bank_contact": config.BLOOD_BANK_EMAIL,
        "blood_bank_phone":  config.BLOOD_BANK_PHONE,
        "message": (
            f"🚨 Blood bank alerted at {config.BLOOD_BANK_EMAIL} "
            "— Emergency team notified!"
        ),
    }


def get_alerts(email: str | None = None, limit: int = 50) -> list[dict]:
    """
    Return recent blood bank alerts.
    If `email` is provided, filter to that patient only.
    """
    if not is_connected():
        return []
    db = get_db()
    query = {"patient_email": email} if email else {}
    cursor = (
        db["blood_bank_alerts"]
        .find(query, {"_id": 0})
        .sort("timestamp", -1)
        .limit(limit)
    )
    return list(cursor)
