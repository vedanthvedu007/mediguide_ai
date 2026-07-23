"""
db/mongo.py — MongoDB Connection Singleton
==========================================
Provides a single shared MongoClient instance across the app.
Configure via MONGO_URI environment variable (see .env.example).

Collections used:
  mediguide.users             — user accounts
  mediguide.patients          — symptom check history
  mediguide.blood_bank_alerts — emergency blood alerts
  mediguide.feedback          — user feedback submissions
"""

import os
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ConfigurationError

_client: MongoClient | None = None
_db = None


def connect() -> None:
    """
    Initialise the MongoDB connection and create indexes.
    Called once at app startup from app.py.
    """
    global _client, _db

    uri = os.environ.get("MONGO_URI", "")
    if not uri:
        raise EnvironmentError(
            "[MongoDB] MONGO_URI is not set.\n"
            "  -> Create a .env file from .env.example and add your MongoDB Atlas URI."
        )

    try:
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Force a round-trip to validate the connection immediately
        _client.admin.command("ping")
        _db = _client["mediguide"]
        _ensure_indexes()
        print("[MongoDB] [OK] Connected to Atlas - database: mediguide")
    except (ConnectionFailure, ConfigurationError) as exc:
        raise ConnectionError(
            f"[MongoDB] [ERROR] Could not connect: {exc}\n"
            "  -> Check your MONGO_URI in the .env file."
        ) from exc


def get_db():
    """Return the active MongoDB database handle."""
    if _db is None:
        raise RuntimeError(
            "[MongoDB] Database not initialised. Call connect() first."
        )
    return _db


def is_connected() -> bool:
    """Return True if database is connected and initialized."""
    return _db is not None


def _ensure_indexes() -> None:
    """Create indexes for performance and uniqueness constraints."""
    db = _db
    # users.email must be unique
    db["users"].create_index([("email", ASCENDING)], unique=True)
    # patients: look up by email + sort by date
    db["patients"].create_index([("email", ASCENDING), ("date", DESCENDING)])
    # alerts: look up by patient_email
    db["blood_bank_alerts"].create_index([("patient_email", ASCENDING)])
    # feedback: look up by email
    db["feedback"].create_index([("email", ASCENDING)])
    print("[MongoDB] [OK] Indexes verified")
