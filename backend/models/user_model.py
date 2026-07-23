"""
models/user_model.py — User Account Model
==========================================
Handles all read/write operations for the `users` collection.

Schema (MongoDB document):
  {
    "_id":        ObjectId,
    "name":       str,
    "email":      str  (unique, lowercase),
    "password":   str  (werkzeug pbkdf2 hash),
    "age":        int | None,
    "created_at": datetime
  }
"""

from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError
from werkzeug.security import generate_password_hash, check_password_hash
from db.mongo import get_db, is_connected


def create_user(name: str, email: str, password: str, age: int | None = None) -> dict:
    """
    Insert a new user.
    Returns {"status": "success"} or {"status": "exists"} or {"status": "error"}.
    """
    if not is_connected():
        return {"status": "error", "message": "Database features are currently offline."}
    db = get_db()
    hashed = generate_password_hash(password)
    doc = {
        "name":       name.strip(),
        "email":      email.strip().lower(),
        "password":   hashed,
        "age":        age,
        "created_at": datetime.now(timezone.utc),
    }
    try:
        db["users"].insert_one(doc)
        return {"status": "success"}
    except DuplicateKeyError:
        return {"status": "exists"}
    except Exception as exc:
        print(f"[UserModel] create_user error: {exc}")
        return {"status": "error", "message": str(exc)}


def find_by_email(email: str) -> dict | None:
    """Return the user document for the given email, or None."""
    if not is_connected():
        return None
    db = get_db()
    return db["users"].find_one({"email": email.strip().lower()})


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if `plain` matches the stored `hashed` password."""
    return check_password_hash(hashed, plain)


def seed_demo_user() -> None:
    """
    Insert the demo user if it does not already exist.
    Called once at app startup.
    """
    existing = find_by_email("demo@mediguide.ai")
    if not existing:
        result = create_user(
            name="Demo User",
            email="demo@mediguide.ai",
            password="health123",
            age=28,
        )
        if result["status"] == "success":
            print("[MongoDB] [OK] Demo user created (demo@mediguide.ai / health123)")
    else:
        print("[MongoDB] [OK] Demo user already exists")
