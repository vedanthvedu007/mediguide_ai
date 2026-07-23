"""
services/ai_service.py — Gemini AI Health Triage
==================================================
Calls Google's Gemini API (gemini-2.0-flash-lite) to generate
enriched health triage responses.  Falls back to rule-based
mode if the API key is missing or the call fails.

Uses Python's built-in urllib — no extra packages required.
"""

import json
import re
import urllib.request
import urllib.error
import config


def call_gemini_ai(conversation_history: list, user_message: str, matched_symptoms: list) -> dict:
    """
    Send symptom context to Gemini and return a structured triage dict.
    Returns None if AI is disabled or the call fails.
    """
    if not config.USE_AI_FALLBACK:
        return None

    system_prompt = (
        "You are MediGuide AI, a compassionate healthcare triage assistant for rural India.\n"
        "Detected symptoms: " + (", ".join(matched_symptoms) if matched_symptoms else "none") + "\n\n"
        "Respond ONLY in this exact JSON (no markdown, no extra text):\n"
        '{\n'
        '  "simple_explanation": "friendly 1-2 sentence explanation with emojis",\n'
        '  "risk_level": "LOW" or "MEDIUM" or "HIGH",\n'
        '  "triage_level": "HOME_CARE" or "CLINIC_VISIT" or "EMERGENCY",\n'
        '  "triage_reason": "brief reason in one sentence",\n'
        '  "home_care_tips": ["tip1", "tip2", "tip3", "tip4", "tip5"],\n'
        '  "warning_signs": ["sign1", "sign2", "sign3"],\n'
        '  "follow_up": "one relevant follow-up question",\n'
        '  "followup_options": ["option1", "option2", "option3"]\n'
        "}\n\n"
        "Rules:\n"
        "- Use specific medicine names and doses (e.g. Paracetamol 500mg)\n"
        "- Include Indian home remedies (tulsi tea, haldi milk, ginger, ajwain)\n"
        "- EMERGENCY only for chest pain+breathlessness, stroke, unconsciousness, severe bleeding\n"
        "- Always mention 108 for emergencies\n"
        "- No text outside the JSON"
    )

    # Build Gemini-format contents from conversation history
    contents = []
    for turn in conversation_history[-6:]:
        role = "model" if turn["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": turn["content"]}]})
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    payload = json.dumps({
        "contents": contents,
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "generationConfig": {
            "maxOutputTokens": 900,
            "temperature": 0.7,
        }
    }).encode("utf-8")

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{config.GEMINI_MODEL}:generateContent"
        f"?key={config.GEMINI_API_KEY}"
    )

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            # Strip markdown code fences if the model wraps output
            text = re.sub(r"^```json\s*|^```\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
            return json.loads(text)

    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        if e.code in (401, 403):
            print(f"[Gemini API] Key invalid or expired (HTTP {e.code}) — switching to rule-based mode")
            config.USE_AI_FALLBACK = False  # disable for this session
        else:
            print(f"[Gemini API error] HTTP {e.code}: {e.reason}")
            if body:
                print(f"[Gemini API error] Body: {body[:300]}")
        return None
    except Exception as e:
        print(f"[Gemini API error] {e}")
        return None
