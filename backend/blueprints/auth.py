"""
blueprints/auth.py — Authentication Routes
===========================================
Provides /login and /register endpoints.
Uses models/user_model.py for all database operations.
Passwords are hashed via werkzeug (pbkdf2:sha256).
"""

from flask import Blueprint, request, jsonify
from models import user_model

auth_bp = Blueprint("auth", __name__)


# ─── POST /login ──────────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate a user.

    Request JSON:  { "email": str, "password": str }
    Response JSON: { "status": "success", "name": str, "email": str, "age": int }
                 | { "status": "fail" }  (HTTP 401)
    """
    data     = request.get_json(silent=True) or {}
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"status": "fail", "message": "Email and password are required"}), 400

    user = user_model.find_by_email(email)
    if user and user_model.verify_password(password, user["password"]):
        return jsonify({
            "status": "success",
            "name":   user["name"],
            "email":  user["email"],
            "age":    user.get("age"),
        })

    return jsonify({"status": "fail", "message": "Invalid email or password"}), 401


# ─── POST /register ───────────────────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Create a new user account.

    Request JSON:  { "name": str, "email": str, "password": str, "age": int? }
    Response JSON: { "status": "success" }
                 | { "status": "exists" }   (HTTP 409)
                 | { "status": "error", "message": str }  (HTTP 400 / 500)
    """
    data     = request.get_json(silent=True) or {}
    name     = data.get("name", "").strip()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")
    age      = data.get("age", None)

    # Basic validation
    if not name or not email or len(password) < 6:
        return jsonify({
            "status":  "error",
            "message": "Name, email, and a password of at least 6 characters are required.",
        }), 400

    result = user_model.create_user(name, email, password, age)

    if result["status"] == "success":
        return jsonify(result), 201
    if result["status"] == "exists":
        return jsonify(result), 409
    return jsonify(result), 500
