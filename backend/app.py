"""
app.py — MediGuide AI Flask Application Entry Point
=====================================================
Bootstraps the app in this order:
  1. Load .env (python-dotenv)
  2. Load ML artifacts (config.py)
  3. Connect to MongoDB (db/mongo.py)
  4. Seed the demo user (models/user_model.py)
  5. Register blueprints
  6. Serve the single-page frontend
"""

import os
from dotenv import load_dotenv

# ── Load .env before any config import ──────────────────────────
load_dotenv()

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

import config                        # ML model loading (after dotenv)
from db.mongo import connect as mongo_connect
from models.user_model import seed_demo_user
from blueprints.auth import auth_bp
from blueprints.api import api_bp

# ── Create Flask app ────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "..", "frontend", "templates"),
    static_folder=os.path.join(BASE_DIR, "..", "frontend", "static")
)
app.secret_key = os.environ.get(
    "SECRET_KEY", "mediguide-dev-secret-2026-change-in-production"
)
CORS(app, resources={r"/*": {"origins": "*"}})

# ── Connect to MongoDB & seed demo user ─────────────────────────
try:
    mongo_connect()
    seed_demo_user()
except Exception as exc:
    print(f"\n[WARN MongoDB] {exc}")
    print("[WARN MongoDB] App will start, but database features are DISABLED.\n")

# ── Register Blueprints ─────────────────────────────────────────
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)


# ── Root Route ──────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def home_route():
    """
    Serves the single-page frontend (index.html via Jinja2).
    Returns JSON status ping if the caller prefers application/json.
    """
    accept       = request.headers.get("Accept", "")
    content_type = request.headers.get("Content-Type", "")

    if "application/json" in accept or content_type == "application/json":
        return jsonify({
            "status":      "MediGuide AI backend running",
            "version":     "3.0",
            "ml_available": config.ML_AVAILABLE,
            "ai_enabled":  config.USE_AI_FALLBACK,
            "ai_provider": f"Gemini ({config.GEMINI_MODEL})" if config.USE_AI_FALLBACK else "Rule-based",
        })

    return render_template("index.html")


# ── Dev Server ──────────────────────────────────────────────────
if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") != "production"

    print("\n" + "=" * 46)
    print("  [MediGuide AI]  -  Backend  v3.0")
    print("=" * 46)
    print(f"  ML Model   : {'[OK] Loaded' if config.ML_AVAILABLE else '[WARN] Rule-Based Fallback'}")
    print(f"  Gemini AI  : {'[OK] ' + config.GEMINI_MODEL if config.USE_AI_FALLBACK else '[WARN] Set GEMINI_API_KEY'}")
    print(f"  Blood Bank : {config.BLOOD_BANK_EMAIL}")
    print(f"  Server     : http://localhost:{port}")
    print("=" * 46 + "\n")

    app.run(debug=debug, host="0.0.0.0", port=port)
