"""
models/feedback_model.py — User Feedback Model
===============================================
Handles all read/write operations for the `feedback` collection.

Schema (MongoDB document):
  {
    "_id":       ObjectId,
    "email":     str,
    "rating":    int  (1–5),
    "liked":     str,
    "improve":   str,
    "recommend": str  ("Yes" | "Maybe" | "No"),
    "date":      str  ("YYYY-MM-DD HH:MM:SS"),
    "timestamp": datetime
  }
"""

from datetime import datetime, timezone
from db.mongo import get_db, is_connected


def save_feedback(
    email: str,
    rating: int,
    liked: str,
    improve: str,
    recommend: str,
) -> dict:
    """
    Insert a feedback submission.
    Returns {"status": "success"} or {"status": "error", "message": ...}.
    """
    if not is_connected():
        return {"status": "error", "message": "Database features are currently offline."}
    db = get_db()
    try:
        db["feedback"].insert_one({
            "email":     email.strip().lower() if email else "anonymous",
            "rating":    int(rating),
            "liked":     liked.strip(),
            "improve":   improve.strip(),
            "recommend": recommend.strip(),
            "date":      datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": datetime.now(timezone.utc),
        })
        return {"status": "success", "message": "Feedback saved successfully."}
    except Exception as exc:
        print(f"[FeedbackModel] save_feedback error: {exc}")
        return {"status": "error", "message": str(exc)}
