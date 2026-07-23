"""
blueprints/api.py — Core API Routes
=====================================
All routes use the models layer (models/) for MongoDB access.
No raw database calls live here — only request parsing, business logic,
and response formatting.

Routes:
  POST  /predict              — AI symptom triage
  GET   /history/<email>      — Patient history
  GET   /blood-bank-alerts    — Blood bank alert log
  GET   /remedies             — Remedy data
  POST  /feedback             — Submit feedback
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timezone

import config
from models import patient_model, alert_model, feedback_model
from services.ai_service import call_gemini_ai
from services.notification_service import send_emergency_alert
from services.triage_service import (
    extract_feature_vector,
    is_health_related,
    rule_based_response,
    pick_remedies,
    REMEDIES,
)

api_bp = Blueprint("api", __name__)


# ─── Helper: Trigger Blood Bank Alert ──────────────────────────
def _trigger_blood_bank_alert(
    patient_email: str,
    patient_name: str,
    symptoms: str,
    risk_score: int,
    triage_level: str,
) -> dict:
    """
    Save an emergency blood bank alert to MongoDB and print a server log.
    Returns the alert info dict to embed in the /predict response.
    """
    alert_info = alert_model.save_alert(
        patient_email=patient_email,
        patient_name=patient_name,
        symptoms=symptoms,
        risk_score=risk_score,
        triage_level=triage_level,
    )

    print(f"\n[BLOOD BANK ALERT]")
    print(f"  Patient  : {patient_name} ({patient_email})")
    print(f"  Symptoms : {symptoms}")
    print(f"  Risk     : {risk_score}/100  |  Triage: {triage_level}")
    print(f"  Notified : {config.BLOOD_BANK_EMAIL}")
    print(f"  Time     : {alert_info['alert_time']}\n")

    # ── Send real Gmail email alert (background thread — non-blocking) ──
    send_emergency_alert(
        patient_name=patient_name,
        patient_email=patient_email,
        symptoms=symptoms,
        risk_score=risk_score,
        triage_level=triage_level,
        to_email=config.BLOOD_BANK_EMAIL,
        smtp_email=config.SMTP_EMAIL,
        smtp_password=config.SMTP_PASSWORD,
    )

    return alert_info


# ─── POST /predict ─────────────────────────────────────────────
@api_bp.route("/predict", methods=["POST"])
def predict():
    """
    Main symptom-triage endpoint.

    Request JSON:
      message              str   — user's symptom text
      email                str   — patient email (for history saving)
      name                 str   — patient name (optional)
      history              list  — conversation history [{role, content}, ...]
      bmi_severity_adjust  int   — extra risk points from BMI panel

    Response JSON: full triage result (see renderBotResponse in chat.js)
    """
    data                 = request.get_json(silent=True) or {}
    user_message         = data.get("message", "").strip()
    email                = data.get("email", "").strip().lower()
    conversation_history = data.get("history", [])
    bmi_severity_adjust  = data.get("bmi_severity_adjust", 0)
    patient_name         = data.get("name", "") or patient_model.get_patient_name(email)

    # ── Non-health question guard ──
    if not is_health_related(user_message):
        return jsonify({
            "simple_explanation": (
                "I am MediGuide AI — I specialise in health questions 🩺 "
                "Please describe your symptoms!"
            ),
            "symptom_icons":   ["❓"],
            "triage_level":    "HOME_CARE",
            "triage_reason":   "Not a health-related question",
            "risk_score":      0,
            "risk_level":      "LOW",
            "matched_symptoms": [],
            "home_care_tips":  ["Please describe what health problem you are experiencing."],
            "warning_signs":   [],
            "follow_up":       "What symptoms are you feeling?",
            "followup_options": ["I have fever", "I have pain", "I feel weak", "I have cough"],
            "blood_bank_alert": None,
        })

    # ── Build full context from conversation history ──
    prior_text   = " ".join(t["content"] for t in conversation_history if t.get("role") == "user")
    full_context = (prior_text + " " + user_message).strip()

    feature_vector, matched_symptoms = extract_feature_vector(full_context)

    # ── ML / Rule-based risk scoring ──
    # ── Explicit Emergency Trigger Check ──
    is_explicit_emergency = False
    lower_msg = user_message.lower()
    if "emergency blood" in lower_msg or "manual blood alert" in lower_msg or "blood required urgent" in lower_msg:
        is_explicit_emergency = True

    risk_label = "LOW"
    risk_pct   = 20

    if config.ML_AVAILABLE and feature_vector is not None:
        try:
            raw_pred   = config.model.predict(feature_vector)[0]
            risk_label = config.encoder.inverse_transform([raw_pred])[0]
            try:
                proba    = config.model.predict_proba(feature_vector)[0]
                classes  = list(config.encoder.classes_)
                hi_idx   = classes.index("HIGH")   if "HIGH"   in classes else 0
                med_idx  = classes.index("MEDIUM") if "MEDIUM" in classes else 2
                risk_pct = min(int(proba[hi_idx] * 100 + proba[med_idx] * 50), 100)
            except Exception:
                risk_pct = {"HIGH": 85, "MEDIUM": 55, "LOW": 20}.get(risk_label, 30)

            # Let percentage be the truth for risk label
            risk_label = "HIGH" if risk_pct >= 70 else "MEDIUM" if risk_pct >= 40 else "LOW"

        except Exception as exc:
            print(f"[ML error] {exc}")
            risk_pct   = min(len(matched_symptoms) * 12, 90)
            risk_label = "HIGH" if risk_pct >= 70 else "MEDIUM" if risk_pct >= 40 else "LOW"
    else:
        risk_pct   = min(len(matched_symptoms) * 10, 35)
        risk_label = "LOW"

    # ── Rule-based Safety Safeguards & Floor Values ──
    HIGH_RISK = {"chest_pain", "breathlessness", "coma",
                 "blood_in_sputum", "stomach_bleeding", "altered_sensorium"}
    MED_RISK  = {"high_fever", "vomiting", "diarrhoea", "fast_heart_rate", "dizziness"}

    if any(s in HIGH_RISK for s in matched_symptoms) or is_explicit_emergency:
        risk_pct   = max(risk_pct, 85)
        risk_label = "HIGH"
    elif any(s in MED_RISK for s in matched_symptoms):
        risk_pct   = max(risk_pct, 55)
        if risk_label == "LOW":
            risk_label = "MEDIUM"

    if bmi_severity_adjust:
        risk_pct = min(risk_pct + int(bmi_severity_adjust), 100)

    # ── Triage level determination ──
    if risk_label == "HIGH" or risk_pct >= 70:
        triage_level  = "EMERGENCY"
        triage_reason = "High-risk symptoms — seek immediate medical attention"
        risk_label    = "HIGH"
    elif risk_label == "MEDIUM" or risk_pct >= 40:
        triage_level  = "CLINIC_VISIT"
        triage_reason = "Moderate symptoms — doctor visit recommended"
        risk_label    = "MEDIUM"
    else:
        triage_level  = "HOME_CARE"
        triage_reason = "Mild symptoms — manageable at home"

    # ── AI response (Gemini) ──
    ai_result = call_gemini_ai(conversation_history, user_message, matched_symptoms)

    if ai_result:
        explanation   = ai_result.get("simple_explanation", "Here is your health guidance.")
        tips          = ai_result.get("home_care_tips", [])
        warnings      = ai_result.get("warning_signs", [])
        follow_up     = ai_result.get("follow_up", "How are you feeling now?")
        followup_opts = ai_result.get("followup_options", ["Better", "Same", "Worse"])
        ai_triage     = ai_result.get("triage_level", "")

        if ai_triage == "EMERGENCY":
            triage_level  = "EMERGENCY"
            triage_reason = ai_result.get("triage_reason", triage_reason)
            risk_pct      = max(risk_pct, 80)
            risk_label    = "HIGH"
        elif ai_triage == "CLINIC_VISIT" and triage_level == "HOME_CARE":
            triage_level  = "CLINIC_VISIT"
            triage_reason = ai_result.get("triage_reason", triage_reason)
            # Bug Fix: sync risk_label when AI upgrades to CLINIC_VISIT
            if risk_label == "LOW":
                risk_label = "MEDIUM"
                risk_pct   = max(risk_pct, 40)
    else:
        rb            = rule_based_response(matched_symptoms, risk_pct, user_message)
        explanation   = rb["simple_explanation"]
        tips          = rb["home_care_tips"]
        warnings      = rb["warning_signs"]
        follow_up     = rb["follow_up"]
        followup_opts = rb["followup_options"]
        triage_level  = rb["triage_level"]
        triage_reason = rb["triage_reason"]
        # Bug Fix: sync risk_label to match rule-based triage level
        if triage_level == "EMERGENCY":
            risk_label = "HIGH"
            risk_pct   = max(risk_pct, 70)
        elif triage_level == "CLINIC_VISIT":
            risk_label = "MEDIUM"
            risk_pct   = max(risk_pct, 40)
        else:
            risk_label = "LOW"

    # ── Merge engine remedies into tips ──
    engine_tips = pick_remedies(matched_symptoms, risk_label)
    if engine_tips and tips:
        combined = list(tips)
        for r in engine_tips:
            if r not in combined:
                combined.append(r)
        tips = combined[:9]
    elif not tips:
        tips = engine_tips

    # ── Recurring symptom escalation ──
    symptom_summary = (
        ", ".join(matched_symptoms) if matched_symptoms else user_message[:120]
    )
    if patient_model.check_recurring(email, symptom_summary) and triage_level == "HOME_CARE":
        triage_level  = "CLINIC_VISIT"
        triage_reason += " — symptoms recurring for multiple days"
        risk_label    = "MEDIUM"
        risk_pct      = max(risk_pct, 40)

    # ── Persist check to MongoDB ──
    patient_model.save_check(email, symptom_summary, risk_pct, triage_level)

    # ── Blood bank alert (for EMERGENCY / HIGH) ──
    blood_bank_alert_info = None
    if triage_level == "EMERGENCY" or risk_label == "HIGH":
        blood_bank_alert_info = _trigger_blood_bank_alert(
            patient_email=email or "unknown",
            patient_name=patient_name or "Unknown Patient",
            symptoms=symptom_summary,
            risk_score=risk_pct,
            triage_level=triage_level,
        )

    # ── Build symptom icon list ──
    ICON_MAP = {
        "high_fever": "🌡️", "mild_fever": "🌡️",
        "headache": "🤕", "cough": "😮‍💨", "phlegm": "😮‍💨",
        "chest_pain": "💔", "breathlessness": "😮",
        "vomiting": "🤢", "nausea": "🤢", "diarrhoea": "🏃",
        "skin_rash": "🔴", "itching": "🔴",
        "joint_pain": "🦴", "muscle_pain": "💪",
        "dizziness": "😵", "fatigue": "😴",
        "back_pain": "🦴", "stomach_pain": "🫃", "abdominal_pain": "🫃",
        "throat_irritation": "🤒", "runny_nose": "🤧", "congestion": "🤧",
    }
    icons = list({ICON_MAP[s] for s in matched_symptoms if s in ICON_MAP}) or ["🩺"]

    return jsonify({
        "simple_explanation": explanation,
        "symptom_icons":      icons[:5],
        "triage_level":       triage_level,
        "triage_reason":      triage_reason,
        "risk_score":         risk_pct,
        "risk_level":         risk_label,
        "matched_symptoms":   [s.replace("_", " ") for s in matched_symptoms],
        "home_care_tips":     tips,
        "warning_signs":      warnings,
        "follow_up":          follow_up,
        "followup_options":   followup_opts,
        "blood_bank_alert":   blood_bank_alert_info,
    })


# ─── GET /history/<email> ──────────────────────────────────────
@api_bp.route("/history/<email>", methods=["GET"])
def history(email: str):
    """Return the last 20 symptom checks for a patient."""
    rows = patient_model.get_history(email.lower(), limit=20)
    return jsonify(rows)


# ─── GET /blood-bank-alerts ────────────────────────────────────
@api_bp.route("/blood-bank-alerts", methods=["GET"])
def blood_bank_alerts_route():
    """Return blood bank alerts (optionally filtered by patient email)."""
    email  = request.args.get("email", None)
    alerts = alert_model.get_alerts(email=email, limit=50)
    return jsonify(alerts)


# ─── GET /remedies ─────────────────────────────────────────────
@api_bp.route("/remedies", methods=["GET"])
def get_remedies():
    """Return the full server-side remedies dictionary."""
    return jsonify(REMEDIES)


# ─── POST /feedback ────────────────────────────────────────────
@api_bp.route("/feedback", methods=["POST"])
def save_feedback_route():
    """
    Save user feedback.

    Request JSON: { email, rating, liked, improve, recommend }
    """
    data    = request.get_json(silent=True) or {}
    result  = feedback_model.save_feedback(
        email     = data.get("email",     "anonymous"),
        rating    = data.get("rating",    0),
        liked     = data.get("liked",     ""),
        improve   = data.get("improve",   ""),
        recommend = data.get("recommend", ""),
    )
    status_code = 200 if result["status"] == "success" else 500
    return jsonify(result), status_code
