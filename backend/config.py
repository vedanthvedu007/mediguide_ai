"""
config.py — Application Configuration
======================================
Loads ML model artifacts and reads environment variables.
python-dotenv is loaded in app.py before this module is imported,
so os.environ.get() calls here will see .env values.
"""

import os
import pickle

# ─────────────────────────────────────────────────────────────────
#  ML ARTIFACTS
# ─────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_DIR = os.path.join(BASE_DIR, "ml_models")

try:
    with open(os.path.join(ML_DIR, "model.pkl"), "rb") as f:
        model = pickle.load(f)
    with open(os.path.join(ML_DIR, "encoder.pkl"), "rb") as f:
        encoder = pickle.load(f)
    with open(os.path.join(ML_DIR, "features.pkl"), "rb") as f:
        FEATURES = pickle.load(f)
    ML_AVAILABLE = True
    print("[MediGuide] [OK] ML model loaded successfully from ml_models/.")
except Exception as exc:
    print(f"[MediGuide] [WARN] ML model not found in ml_models/ ({exc}). Using rule-based fallback.")
    ML_AVAILABLE = False
    model = encoder = FEATURES = None

# ─────────────────────────────────────────────────────────────────
#  GEMINI (Google AI) — AI FALLBACK
# ─────────────────────────────────────────────────────────────────
GEMINI_API_KEY  = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL    = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-lite")
USE_AI_FALLBACK = bool(GEMINI_API_KEY)

if USE_AI_FALLBACK:
    print(f"[MediGuide] [OK] Gemini AI key found - AI responses enabled (model: {GEMINI_MODEL}).")
else:
    print("[MediGuide] [WARN] No GEMINI_API_KEY - using rule-based responses.")

# ─────────────────────────────────────────────────────────────────
#  BLOOD BANK CONTACT
# ─────────────────────────────────────────────────────────────────
BLOOD_BANK_EMAIL = os.environ.get("BLOOD_BANK_EMAIL", "bloodbank@hospital.com")
BLOOD_BANK_PHONE = os.environ.get("BLOOD_BANK_PHONE", "+91-XXXXXXXXXX")

# ─────────────────────────────────────────────────────────────────
#  GMAIL SMTP — Emergency Email Notifications
# ─────────────────────────────────────────────────────────────────
# SMTP_EMAIL    = your Gmail address (e.g. youremail@gmail.com)
# SMTP_PASSWORD = Google App Password (NOT your normal Gmail password)
#   Steps: myaccount.google.com → Security → App Passwords → create one
SMTP_EMAIL    = os.environ.get("SMTP_EMAIL", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")

if SMTP_EMAIL and SMTP_PASSWORD:
    print(f"[MediGuide] [OK] Gmail SMTP configured — alerts will email {BLOOD_BANK_EMAIL}")
else:
    print("[MediGuide] [WARN] SMTP_EMAIL / SMTP_PASSWORD not set — email alerts disabled")
