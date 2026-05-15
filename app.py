"""
MediGuide AI — Merged Backend
Flask server with ML triage, NLP symptom extraction, remedy engine,
multi-turn Claude AI chat, auth, and patient history.

Run:
    pip install flask flask-cors numpy scikit-learn xgboost
    python app.py

Required files (same folder): model.pkl, encoder.pkl, features.pkl
Optional: set env var ANTHROPIC_API_KEY=sk-ant-... for AI-powered responses
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np
import sqlite3
from datetime import datetime
import pickle
import re
import json
import os
import urllib.request

# ─────────────────────────────────────────
#  LOAD ML ARTIFACTS
# ─────────────────────────────────────────
try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("encoder.pkl", "rb") as f:
        encoder = pickle.load(f)
    with open("features.pkl", "rb") as f:
        FEATURES = pickle.load(f)
    ML_AVAILABLE = True
    print("[MediGuide] ML model loaded successfully.")
except Exception as e:
    print(f"[MediGuide] WARNING: ML model not found ({e}). Using rule-based only.")
    ML_AVAILABLE = False
    model = encoder = FEATURES = None

app = Flask(__name__)
CORS(app)  # Allow all origins — restrict in production

# ─────────────────────────────────────────
#  ANTHROPIC CONFIG
#  Set env var: ANTHROPIC_API_KEY=sk-ant-...
# ─────────────────────────────────────────
GROK_API_KEY = os.environ.get("GROK_API_KEY", "")
USE_AI_FALLBACK = bool(GROK_API_KEY)
if USE_AI_FALLBACK:
    print("[MediGuide] Grok API key found — AI fallback enabled.")
else:
    print("[MediGuide] No Grok API key — using rule-based responses.")


# ─────────────────────────────────────────
#  DATABASE
# ─────────────────────────────────────────
def get_db():
    return sqlite3.connect("patients.db")

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            age INTEGER
        )
    """)

    # Safe migration for existing DBs
    c.execute("PRAGMA table_info(users)")
    user_cols = [row[1] for row in c.fetchall()]
    if "age" not in user_cols:
        c.execute("ALTER TABLE users ADD COLUMN age INTEGER")

    c.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            symptoms TEXT,
            risk INTEGER,
            triage_level TEXT,
            date TEXT
        )
    """)

    c.execute("PRAGMA table_info(patients)")
    pat_cols = [row[1] for row in c.fetchall()]
    if "triage_level" not in pat_cols:
        c.execute("ALTER TABLE patients ADD COLUMN triage_level TEXT")

    conn.commit()
    conn.close()

init_db()


# ─────────────────────────────────────────
#  SYMPTOM KEYWORD MAP  (NLP extraction)
# ─────────────────────────────────────────
SYMPTOM_KEYWORDS = {
    "itching":                      ["itch", "itching", "itchy"],
    "skin_rash":                    ["rash", "skin rash", "skin eruption", "red skin"],
    "nodal_skin_eruptions":         ["nodal eruption", "skin nodule"],
    "continuous_sneezing":          ["sneeze", "sneezing", "continuous sneeze"],
    "shivering":                    ["shiver", "shivering", "trembling", "shaking"],
    "chills":                       ["chill", "chills", "cold feeling", "feel cold"],
    "joint_pain":                   ["joint pain", "joint ache", "joints hurt"],
    "stomach_pain":                 ["stomach pain", "stomach ache", "tummy pain"],
    "acidity":                      ["acidity", "acid reflux", "heartburn", "sour stomach"],
    "ulcers_on_tongue":             ["tongue ulcer", "mouth ulcer"],
    "muscle_wasting":               ["muscle wasting", "muscle loss"],
    "vomiting":                     ["vomit", "vomiting", "throwing up", "puke"],
    "burning_micturition":          ["burning urination", "burning pee", "pain urination", "burning when urinating"],
    "spotting_urination":           ["spotting urine", "blood in urine"],
    "fatigue":                      ["fatigue", "tired", "exhausted", "no energy", "exhaustion"],
    "weight_gain":                  ["weight gain", "gaining weight"],
    "anxiety":                      ["anxiety", "anxious", "nervous", "panic"],
    "cold_hands_and_feets":         ["cold hands", "cold feet", "cold extremities"],
    "mood_swings":                  ["mood swing", "mood changes", "emotional"],
    "weight_loss":                  ["weight loss", "losing weight", "lost weight"],
    "restlessness":                 ["restless", "restlessness", "cannot rest"],
    "lethargy":                     ["lethargy", "lethargic", "sluggish"],
    "patches_in_throat":            ["throat patch", "white patch throat"],
    "irregular_sugar_level":        ["blood sugar", "irregular sugar", "glucose"],
    "cough":                        ["cough", "coughing", "dry cough", "wet cough"],
    "high_fever":                   ["high fever", "very high fever", "severe fever", "104", "103"],
    "sunken_eyes":                  ["sunken eyes", "hollow eyes"],
    "breathlessness":               ["breathless", "shortness of breath", "cannot breathe",
                                     "difficulty breathing", "breathing problem", "no breath"],
    "sweating":                     ["sweat", "sweating", "night sweat", "excessive sweating"],
    "dehydration":                  ["dehydrated", "dehydration", "dry mouth", "very thirsty"],
    "indigestion":                  ["indigestion", "digestion problem"],
    "headache":                     ["headache", "head pain", "head hurts", "migraine",
                                     "head ache", "head throbbing"],
    "yellowish_skin":               ["yellow skin", "yellowish skin", "jaundice skin"],
    "dark_urine":                   ["dark urine", "brown urine", "dark pee"],
    "nausea":                       ["nausea", "nauseated", "feeling sick", "queasy", "want to vomit"],
    "loss_of_appetite":             ["no appetite", "loss of appetite", "not eating", "no hunger"],
    "pain_behind_the_eyes":         ["eye pain", "pain behind eyes", "eyes hurt"],
    "back_pain":                    ["back pain", "backache", "lower back pain", "back hurts"],
    "constipation":                 ["constipation", "constipated", "hard stool", "no bowel movement"],
    "abdominal_pain":               ["abdominal pain", "abdomen pain", "belly pain", "gut pain"],
    "diarrhoea":                    ["diarrhea", "diarrhoea", "loose motion", "loose stool",
                                     "watery stool", "runny stool"],
    "mild_fever":                   ["mild fever", "low grade fever", "slight fever", "fever", "temperature"],
    "yellow_urine":                 ["yellow urine", "dark yellow urine"],
    "yellowing_of_eyes":            ["yellow eyes", "jaundice eyes", "eyes turning yellow"],
    "acute_liver_failure":          ["liver failure", "liver problem"],
    "fluid_overload":               ["fluid retention", "water retention"],
    "swelling_of_stomach":          ["stomach swelling", "bloated stomach", "belly swollen"],
    "swelled_lymph_nodes":          ["swollen lymph node", "swollen gland", "lymph node"],
    "malaise":                      ["malaise", "generally unwell", "feeling unwell", "not feeling well"],
    "blurred_and_distorted_vision": ["blurred vision", "blurry vision", "vision problem", "double vision"],
    "phlegm":                       ["phlegm", "mucus", "sputum", "thick mucus"],
    "throat_irritation":            ["throat irritation", "scratchy throat", "sore throat", "throat pain"],
    "redness_of_eyes":              ["red eyes", "pink eye", "eye redness"],
    "sinus_pressure":               ["sinus", "sinus pressure", "sinusitis"],
    "runny_nose":                   ["runny nose", "nose running", "nasal drip"],
    "congestion":                   ["congestion", "stuffy nose", "blocked nose"],
    "chest_pain":                   ["chest pain", "chest tight", "chest pressure", "chest hurts",
                                     "heart pain", "chest ache", "chest discomfort"],
    "weakness_in_limbs":            ["weak limbs", "arms weak", "legs weak", "limb weakness"],
    "fast_heart_rate":              ["fast heart rate", "heart racing", "rapid heart", "heart pounding"],
    "pain_during_bowel_movements":  ["pain during bowel", "painful stool", "pain when pooping"],
    "pain_in_anal_region":          ["anal pain", "rectal pain"],
    "bloody_stool":                 ["blood in stool", "bloody stool", "rectal bleeding"],
    "irritation_in_anus":           ["anal irritation", "itchy anus"],
    "neck_pain":                    ["neck pain", "neck ache", "stiff neck pain", "neck hurts"],
    "dizziness":                    ["dizzy", "dizziness", "lightheaded", "spinning", "vertigo"],
    "cramps":                       ["cramp", "cramps", "muscle cramp", "stomach cramp", "leg cramp"],
    "bruising":                     ["bruise", "bruising", "bruised easily"],
    "obesity":                      ["obese", "obesity", "very overweight"],
    "swollen_legs":                 ["swollen legs", "leg swelling", "swollen ankles"],
    "puffy_face_and_eyes":          ["puffy face", "puffy eyes", "face swollen"],
    "enlarged_thyroid":             ["thyroid", "enlarged thyroid", "goitre", "neck lump"],
    "brittle_nails":                ["brittle nails", "nails breaking"],
    "excessive_hunger":             ["excessive hunger", "always hungry", "constant hunger"],
    "drying_and_tingling_lips":     ["tingling lips", "dry lips"],
    "slurred_speech":               ["slurred speech", "cannot speak clearly"],
    "knee_pain":                    ["knee pain", "knees hurt"],
    "hip_joint_pain":               ["hip pain", "hip joint pain"],
    "muscle_weakness":              ["muscle weakness", "weak muscles"],
    "stiff_neck":                   ["stiff neck", "neck stiffness"],
    "swelling_joints":              ["swollen joints", "joint swelling"],
    "movement_stiffness":           ["stiffness", "movement stiff", "rigid muscles"],
    "spinning_movements":           ["spinning", "balance problem"],
    "loss_of_balance":              ["loss of balance", "unsteady"],
    "unsteadiness":                 ["wobbly", "unsteadiness"],
    "weakness_of_one_body_side":    ["one side weak", "half body weak"],
    "loss_of_smell":                ["loss of smell", "cannot smell"],
    "bladder_discomfort":           ["bladder pain", "bladder discomfort", "pelvic pain"],
    "continuous_feel_of_urine":     ["frequent urination", "urge to urinate", "urinating often"],
    "passage_of_gases":             ["gas", "flatulence", "passing gas", "bloating", "bloated"],
    "depression":                   ["depression", "depressed", "very sad", "hopeless"],
    "irritability":                 ["irritable", "irritability", "easily angered"],
    "muscle_pain":                  ["muscle pain", "muscle ache", "body ache", "body pain",
                                     "muscles hurt", "myalgia"],
    "altered_sensorium":            ["confused", "confusion", "disoriented", "altered consciousness"],
    "red_spots_over_body":          ["red spots", "red dots", "spots on body"],
    "belly_pain":                   ["belly pain", "belly ache"],
    "abnormal_menstruation":        ["irregular period", "menstruation problem", "period pain"],
    "watering_from_eyes":           ["watery eyes", "eyes watering", "tearing"],
    "increased_appetite":           ["increased appetite", "eating more", "always eating"],
    "polyuria":                     ["urinating a lot", "excessive urination"],
    "lack_of_concentration":        ["cannot concentrate", "brain fog", "cannot focus"],
    "visual_disturbances":          ["visual disturbance", "seeing things"],
    "coma":                         ["unconscious", "coma", "unresponsive"],
    "stomach_bleeding":             ["stomach bleeding", "internal bleeding", "blood vomit"],
    "distention_of_abdomen":        ["distended abdomen", "swollen belly"],
    "blood_in_sputum":              ["blood in sputum", "coughing blood", "blood cough"],
    "palpitations":                 ["palpitation", "heart flutter", "irregular heartbeat", "heart skip"],
    "painful_walking":              ["painful walking", "pain when walking"],
    "blister":                      ["blister", "blisters", "skin blister"],
    "skin_peeling":                 ["skin peeling", "peeling skin"],
    "pus_filled_pimples":           ["pus pimple", "pimple with pus", "acne pus"],
}


# ─────────────────────────────────────────
#  REMEDY DATABASE
# ─────────────────────────────────────────
REMEDIES = {
    "fever": [
        "💊 Take Paracetamol 500mg every 6 hours (max 4 doses/day)",
        "💧 Drink 8-10 glasses of water or ORS solution to stay hydrated",
        "🧊 Apply damp cool cloth on forehead to bring temperature down",
        "🛌 Rest in a cool, well-ventilated room — wear light clothing",
        "🌿 Tulsi + ginger tea with honey — natural fever remedy",
        "⚠️ Fever above 103°F or lasting 3+ days → visit doctor immediately"
    ],
    "headache": [
        "💊 Take Paracetamol 500mg or Ibuprofen 400mg for pain relief",
        "🌑 Rest in a dark, quiet room — light and noise worsen migraines",
        "🧊 Apply cold compress on forehead or warm compress on back of neck",
        "💧 Drink water — dehydration is a very common headache cause",
        "🌿 Peppermint oil on temples or ginger tea helps naturally",
        "⚠️ Sudden severe 'thunderclap' headache → emergency immediately"
    ],
    "cough": [
        "🍯 1 tsp honey + ginger juice in warm water — soothes dry cough",
        "♨️ Steam inhalation 2-3x daily with a few drops of eucalyptus oil",
        "💊 OTC: Benadryl (dry cough) or Grilinctus (wet/productive cough)",
        "🧂 Gargle warm salt water (½ tsp in warm water) 3x daily",
        "❄️ Avoid cold drinks, ice cream, and direct air conditioning",
        "🌿 Mulethi (licorice root) in warm water soothes throat",
        "⚠️ Coughing blood or lasting 2+ weeks → see doctor"
    ],
    "chest_pain": [
        "🚨 Chest pain can be a medical emergency — do NOT ignore or wait",
        "📞 Call 108 immediately if pain is crushing, squeezing, or radiates to arm/jaw",
        "🪑 Sit upright — do NOT lie flat, stay calm and breathe slowly",
        "🚗 Do NOT drive yourself to hospital — call for help",
        "💊 Chew 1 aspirin (325mg) if heart attack suspected and not allergic",
        "⚠️ Any chest pain + sweating + arm pain = call 108 NOW"
    ],
    "breathlessness": [
        "🚨 Sudden or severe breathlessness → call 108 immediately",
        "🪑 Sit upright — lying flat worsens breathing difficulty",
        "💨 Use prescribed inhaler if you have asthma or COPD",
        "🫁 Pursed lip breathing: inhale through nose, exhale slowly through pursed lips",
        "🌬️ Open a window for fresh air — move away from smoke/dust",
        "⚠️ Cannot speak due to breathlessness → emergency immediately"
    ],
    "vomiting": [
        "⏸️ Stop eating solid food for 1-2 hours after vomiting episode",
        "💧 Sip small amounts of ORS or clear liquid every 5-10 minutes",
        "🍚 Eat bland food when tolerated: rice water, khichdi, banana, toast",
        "💊 Domperidone 10mg (Vomikind) for nausea — available OTC",
        "🌿 Ginger tea or ginger candy helps reduce nausea naturally",
        "⚠️ Vomiting blood or lasting 24+ hours → see doctor immediately"
    ],
    "diarrhoea": [
        "💧 Drink ORS (1 packet in 1L water) — replace lost electrolytes urgently",
        "🍚 BRAT diet: Banana, Rice, Applesauce, Toast — easy to digest",
        "🚫 Avoid milk, coffee, fatty food, and spicy food until stools normalize",
        "💊 Loperamide (Imodium) 2mg — reduces frequency of loose motions",
        "🌿 Buttermilk with a pinch of cumin (jeera) and salt helps recovery",
        "⚠️ Blood in stool or lasting 2+ days → visit clinic"
    ],
    "body_pain": [
        "💊 Ibuprofen 400mg or Paracetamol 500mg for muscle and body ache",
        "🌡️ Apply warm compress or hot water bag on sore muscle areas",
        "🛌 Rest and avoid heavy physical activity until pain reduces",
        "🧘 Light gentle stretching reduces muscle stiffness significantly",
        "🥛 Turmeric milk (haldi doodh) — excellent natural anti-inflammatory",
        "🌿 Epsom salt bath or warm water soak relieves joint and muscle pain"
    ],
    "skin_rash": [
        "🚫 Do NOT scratch — scratching worsens rash and risks bacterial infection",
        "🧴 Apply calamine lotion to soothe itching and redness",
        "💊 Cetirizine 10mg (Cetzine) antihistamine if rash is itchy",
        "🔍 Identify and avoid trigger: new soap, food, fabric, or plant contact",
        "🌿 Aloe vera gel applied directly soothes most minor skin rashes",
        "⚠️ Rapidly spreading rash, blisters, or associated fever → doctor immediately"
    ],
    "sore_throat": [
        "🧂 Gargle warm salt water (½ tsp salt in 1 glass warm water) every 4 hours",
        "🍯 Honey + ginger in warm water soothes throat pain effectively",
        "💊 Strepsils lozenges or Betadine Gargle for throat discomfort",
        "❄️ Avoid cold drinks, ice cream, and cold air",
        "🌿 Turmeric milk at bedtime reduces throat inflammation overnight",
        "⚠️ White patches on throat or unable to swallow → visit clinic"
    ],
    "stomach_pain": [
        "🌿 Ajwain (carom seeds) in warm water reduces stomach cramps effectively",
        "💊 Antacids (Gelusil, Eno) if acidity/heartburn is the cause",
        "🍵 Peppermint or fennel (saunf) tea relieves gas and bloating",
        "🛌 Rest and avoid eating until pain reduces",
        "🚫 Avoid spicy, oily, and heavy food during stomach pain",
        "⚠️ Severe pain with fever or vomiting blood → emergency care"
    ],
    "back_pain": [
        "🌡️ Apply warm compress or heating pad on lower back for 15-20 min",
        "💊 Ibuprofen 400mg reduces inflammation and pain in back",
        "🧘 Gentle knee-to-chest stretch while lying flat helps lower back",
        "🪑 Maintain proper posture — avoid slouching or hunching forward",
        "🌿 Mustard oil massage gently on the affected area reduces stiffness",
        "⚠️ Back pain with leg numbness or loss of bladder control → emergency"
    ],
    "dizziness": [
        "🪑 Sit or lie down immediately to prevent falls when dizzy",
        "💧 Drink water or electrolyte drink — dehydration causes dizziness",
        "🍬 Have a small snack if low blood sugar is suspected",
        "🌿 Ginger tea or ginger candy helps reduce dizziness and nausea",
        "🧂 A small glass of ORS or nimbu pani (lemon water with salt) helps",
        "⚠️ Sudden severe dizziness with chest pain or vision problems → 108"
    ],
    "general": [
        "🛌 Rest well — your body heals fastest during sleep (7-8 hours)",
        "💧 Drink 8-10 glasses of water daily to flush toxins",
        "🥗 Eat light, nutritious food: khichdi, soup, dal, fresh fruits",
        "🌿 Tulsi tea or warm honey-ginger water boosts immunity naturally",
        "🌡️ Monitor your temperature and symptoms twice daily",
        "⚠️ If symptoms worsen within 24 hours, visit a doctor promptly"
    ]
}

EMERGENCY_TIPS = [
    "🚨 CALL 108 (Ambulance) IMMEDIATELY — do not wait",
    "🚗 Do NOT drive yourself to hospital — call for help or wait for ambulance",
    "🪑 Keep patient seated or in recovery position (on their side)",
    "🚫 Do not give food, water, or any medication unless directed by 108 operator",
    "🕐 Note the exact time symptoms started — tell the doctor on arrival",
    "📞 Stay on the line with 108 operator — follow their instructions"
]


def pick_remedies(matched: list, risk_label: str) -> list:
    if risk_label == "HIGH":
        return EMERGENCY_TIPS

    sym_map = {
        "high_fever": "fever", "mild_fever": "fever",
        "headache": "headache",
        "cough": "cough", "phlegm": "cough", "mucoid_sputum": "cough",
        "chest_pain": "chest_pain",
        "breathlessness": "breathlessness",
        "vomiting": "vomiting", "nausea": "vomiting",
        "diarrhoea": "diarrhoea",
        "muscle_pain": "body_pain", "joint_pain": "body_pain",
        "skin_rash": "skin_rash", "itching": "skin_rash",
        "throat_irritation": "sore_throat",
        "stomach_pain": "stomach_pain", "abdominal_pain": "stomach_pain",
        "back_pain": "back_pain",
        "dizziness": "dizziness",
    }

    seen = set()
    tips = []
    for sym in matched:
        category = sym_map.get(sym)
        if category and category not in seen:
            seen.add(category)
            tips.extend(REMEDIES.get(category, []))

    if not tips:
        tips = REMEDIES["general"]

    return tips[:8]


# ─────────────────────────────────────────
#  NLP — FEATURE EXTRACTION
# ─────────────────────────────────────────
def extract_feature_vector(text: str):
    text_lower = text.lower()
    matched = []

    for feature, keywords in SYMPTOM_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                matched.append(feature)
                break

    if ML_AVAILABLE and FEATURES:
        vec = np.zeros((1, len(FEATURES)))
        for sym in matched:
            if sym in FEATURES:
                vec[0][FEATURES.index(sym)] = 1
        return vec, matched
    else:
        return None, matched


def is_health_related(text: str) -> bool:
    health_keywords = [
        "pain", "ache", "fever", "cough", "cold", "headache", "sick", "ill", "hurt",
        "vomit", "nausea", "dizzy", "tired", "fatigue", "rash", "itch", "swell",
        "breath", "chest", "stomach", "back", "joint", "muscle", "throat", "nose",
        "eye", "ear", "skin", "bleed", "weak", "faint", "cramp", "burn", "infection",
        "medicine", "doctor", "hospital", "symptom", "disease", "health", "medical",
        "diabetes", "pressure", "bp", "sugar", "heart", "kidney", "liver", "lung",
        "help", "problem", "issue", "feeling", "not well", "unwell", "what", "how",
        "should", "can", "i have", "i am", "my", "bmi", "weight", "height"
    ]
    text_low = text.lower()
    return any(kw in text_low for kw in health_keywords)


# ─────────────────────────────────────────
#  GROK AI CALL  (via urllib — no SDK needed)
# ─────────────────────────────────────────
def call_grok_ai(conversation_history: list, user_message: str, matched_symptoms: list) -> dict:
    if not USE_AI_FALLBACK:
        return None

    system_prompt = """You are MediGuide AI, a compassionate healthcare triage assistant.
Your role:
1. Analyse symptoms described in simple language
2. Give a clear, friendly explanation of possible causes
3. Recommend practical home remedies with specific medicine names and doses
4. Suggest Indian home remedies (tulsi, ginger, haldi, ajwain, etc.) where appropriate
5. Tell patient when to visit clinic vs call emergency 108
6. Ask a relevant follow-up question to gather more information

Already detected symptoms: """ + (", ".join(matched_symptoms) if matched_symptoms else "none") + """

Respond ONLY in this exact JSON (no markdown, no extra text):
{
  "simple_explanation": "friendly explanation in 1-2 sentences with emojis",
  "risk_level": "LOW" or "MEDIUM" or "HIGH",
  "triage_level": "HOME_CARE" or "CLINIC_VISIT" or "EMERGENCY",
  "triage_reason": "brief reason in one sentence",
  "home_care_tips": ["tip with medicine or remedy", "tip2", "tip3", "tip4", "tip5"],
  "warning_signs": ["warning sign 1", "warning sign 2", "warning sign 3"],
  "follow_up": "one relevant follow-up question",
  "followup_options": ["option1", "option2", "option3"]
}

Rules:
- Mention specific medicines by name and dose (e.g. Paracetamol 500mg, not just 'take medicine')
- Include Indian home remedies: tulsi tea, haldi milk, ginger, ajwain water etc.
- EMERGENCY only for: chest pain + breathlessness, stroke signs, unconsciousness, severe bleeding
- Always mention 108 for emergencies
- Be warm and simple — many patients are not medically trained
- Do not add any text outside the JSON"""

    messages = []
    for turn in conversation_history[-6:]:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": user_message})

    # Build messages in OpenAI format (xAI is OpenAI-compatible)
    messages_with_system = [{"role": "system", "content": system_prompt}]
    for turn in conversation_history[-6:]:
        messages_with_system.append({"role": turn["role"], "content": turn["content"]})
    messages_with_system.append({"role": "user", "content": user_message})

    payload = json.dumps({
        "model": "grok-3-mini",
        "max_tokens": 900,
        "messages": messages_with_system
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.x.ai/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROK_API_KEY}"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            text = result["choices"][0]["message"]["content"].strip()
            text = re.sub(r"^```json\s*|^```\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
            return json.loads(text)
    except Exception as e:
        print(f"[Grok API error] {e}")
        return None


# ─────────────────────────────────────────
#  RULE-BASED RESPONSE  (fallback)
# ─────────────────────────────────────────
def rule_based_response(matched: list, risk_score: int) -> dict:
    if risk_score >= 70:
        return {
            "simple_explanation": "⚠️ Your symptoms look serious. Please seek medical help right away. Call 108 if needed.",
            "triage_level": "EMERGENCY",
            "triage_reason": "High-risk symptoms detected — immediate medical attention needed",
            "home_care_tips": EMERGENCY_TIPS,
            "warning_signs": ["Difficulty breathing", "Chest pain or pressure", "Loss of consciousness"],
            "follow_up": "Are you having chest pain or difficulty breathing right now?",
            "followup_options": ["Yes, chest pain", "Yes, breathing difficulty", "Both"]
        }
    elif risk_score >= 40:
        return {
            "simple_explanation": "⚠️ You have moderate symptoms. It is best to see a doctor soon for proper diagnosis.",
            "triage_level": "CLINIC_VISIT",
            "triage_reason": "Moderate symptoms detected — professional evaluation recommended",
            "home_care_tips": pick_remedies(matched, "MEDIUM"),
            "warning_signs": ["Symptoms suddenly worsen", "High fever over 3 days", "Unable to eat or drink"],
            "follow_up": "How long have you had these symptoms?",
            "followup_options": ["Started today", "2-3 days", "More than 3 days"]
        }
    else:
        return {
            "simple_explanation": "😊 Your symptoms appear mild. You can manage at home with rest and these remedies.",
            "triage_level": "HOME_CARE",
            "triage_reason": "Mild symptoms — home care is sufficient for now",
            "home_care_tips": pick_remedies(matched, "LOW"),
            "warning_signs": ["Fever rises above 102°F", "Symptoms suddenly worsen", "New symptoms appear"],
            "follow_up": "Are you experiencing any other symptoms?",
            "followup_options": ["Fever", "Headache", "Body pain", "No other symptoms"]
        }


# ─────────────────────────────────────────
#  DB HELPERS
# ─────────────────────────────────────────
def save_patient(email, symptoms, risk, triage_level):
    if not email:
        return
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO patients (email, symptoms, risk, triage_level, date) VALUES (?,?,?,?,?)",
        (email, symptoms, risk, triage_level, str(datetime.now().date()))
    )
    conn.commit()
    conn.close()


def check_recurring(email, symptoms):
    if not email:
        return False
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT symptoms, date FROM patients WHERE email=? ORDER BY id DESC LIMIT 5",
        (email,)
    )
    rows = c.fetchall()
    conn.close()
    today = datetime.now().date()
    for prev_sym, prev_date_str in rows:
        try:
            prev_date = datetime.strptime(prev_date_str, "%Y-%m-%d").date()
            if prev_sym == symptoms and (today - prev_date).days >= 2:
                return True
        except Exception:
            pass
    return False


# ─────────────────────────────────────────
#  AUTH ROUTES
# ─────────────────────────────────────────
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT id, name, email, age FROM users WHERE email=? AND password=?",
        (email, password)
    )
    user = c.fetchone()
    conn.close()
    if user:
        return jsonify({"status": "success", "name": user[1], "email": user[2], "age": user[3]})
    return jsonify({"status": "fail"}), 401


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    age = data.get("age", None)
    if not name or not email or len(password) < 6:
        return jsonify({"status": "error", "message": "Invalid input"}), 400
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (name, email, password, age) VALUES (?,?,?,?)",
            (name, email, password, age)
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    except Exception:
        conn.close()
        return jsonify({"status": "exists"})


@app.route("/history/<email>", methods=["GET"])
def history(email):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT symptoms, risk, triage_level, date FROM patients WHERE email=? ORDER BY id DESC LIMIT 20",
        (email.lower(),)
    )
    rows = c.fetchall()
    conn.close()
    return jsonify([
        {"symptoms": r[0], "risk": r[1], "triage_level": r[2], "date": r[3]}
        for r in rows
    ])


# ─────────────────────────────────────────
#  MAIN PREDICT / MULTI-TURN CHAT ROUTE
# ─────────────────────────────────────────
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    user_message         = data.get("message", "").strip()
    email                = data.get("email", "").strip().lower()
    conversation_history = data.get("history", [])
    age                  = data.get("age", None)
    bmi                  = data.get("bmi", None)
    bmi_category         = data.get("bmi_category", "")
    bmi_severity_adjust  = data.get("bmi_severity_adjust", 0)

    # Non-health filter
    if not is_health_related(user_message):
        return jsonify({
            "simple_explanation": "I am MediGuide AI — I specialise in health questions 🩺 Please describe your symptoms and I will help you right away!",
            "symptom_icons": ["❓"],
            "triage_level": "HOME_CARE",
            "triage_reason": "Not a health-related question",
            "risk_score": 0,
            "risk_level": "LOW",
            "matched_symptoms": [],
            "home_care_tips": ["Please describe what health problem you are experiencing."],
            "warning_signs": [],
            "follow_up": "What symptoms are you feeling?",
            "followup_options": ["I have fever", "I have pain", "I feel weak", "I have cough"]
        })

    # Build full context for NLP
    prior_user_text = " ".join(
        t["content"] for t in conversation_history if t.get("role") == "user"
    )
    full_context = (prior_user_text + " " + user_message).strip()

    # Step 1 — NLP keyword extraction
    feature_vector, matched_symptoms = extract_feature_vector(full_context)

    # Step 2 — ML prediction (if available)
    risk_label = "LOW"
    risk_pct = 20

    if ML_AVAILABLE and feature_vector is not None:
        try:
            raw_pred = model.predict(feature_vector)[0]
            risk_label = encoder.inverse_transform([raw_pred])[0]
            try:
                proba = model.predict_proba(feature_vector)[0]
                classes = list(encoder.classes_)
                hi_idx = classes.index("HIGH") if "HIGH" in classes else 0
                med_idx = classes.index("MEDIUM") if "MEDIUM" in classes else 2
                risk_pct = min(int(proba[hi_idx] * 100 + proba[med_idx] * 50), 100)
            except Exception:
                risk_pct = {"HIGH": 85, "MEDIUM": 55, "LOW": 20}.get(risk_label, 30)
        except Exception as e:
            print(f"[ML error] {e}")
            # Fallback to keyword counting
            risk_pct = min(len(matched_symptoms) * 12, 90)
            risk_label = "HIGH" if risk_pct >= 70 else "MEDIUM" if risk_pct >= 40 else "LOW"
    else:
        # No ML — keyword-count heuristic
        HIGH_RISK_KEYWORDS = {"chest_pain", "breathlessness", "coma", "blood_in_sputum",
                               "stomach_bleeding", "altered_sensorium"}
        MED_RISK_KEYWORDS  = {"high_fever", "vomiting", "diarrhoea", "fast_heart_rate", "dizziness"}
        if any(s in HIGH_RISK_KEYWORDS for s in matched_symptoms):
            risk_label, risk_pct = "HIGH", 85
        elif any(s in MED_RISK_KEYWORDS for s in matched_symptoms):
            risk_label, risk_pct = "MEDIUM", 55
        else:
            risk_pct = min(len(matched_symptoms) * 10, 35)
            risk_label = "LOW"

    # Apply BMI severity adjustment
    if bmi_severity_adjust:
        risk_pct = min(risk_pct + int(bmi_severity_adjust), 100)

    # Step 3 — Triage
    if risk_label == "HIGH" or risk_pct >= 70:
        triage_level  = "EMERGENCY"
        triage_reason = "High-risk symptoms detected — seek immediate medical attention"
        risk_label    = "HIGH"
    elif risk_label == "MEDIUM" or risk_pct >= 40:
        triage_level  = "CLINIC_VISIT"
        triage_reason = "Moderate symptoms — doctor visit recommended"
        risk_label    = "MEDIUM"
    else:
        triage_level  = "HOME_CARE"
        triage_reason = "Mild symptoms — manageable at home with care"

    # Step 4 — AI or rule-based response
    ai_result = None
    if USE_AI_FALLBACK:
        ai_result = call_grok_ai(conversation_history, user_message, matched_symptoms)

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
        elif ai_triage == "CLINIC_VISIT" and triage_level == "HOME_CARE":
            triage_level  = "CLINIC_VISIT"
            triage_reason = ai_result.get("triage_reason", triage_reason)
    else:
        rb            = rule_based_response(matched_symptoms, risk_pct)
        explanation   = rb["simple_explanation"]
        tips          = rb["home_care_tips"]
        warnings      = rb["warning_signs"]
        follow_up     = rb["follow_up"]
        followup_opts = rb["followup_options"]
        triage_level  = rb["triage_level"]
        triage_reason = rb["triage_reason"]

    # Step 5 — Merge remedy engine tips
    engine_tips = pick_remedies(matched_symptoms, risk_label)
    if engine_tips and tips:
        combined = list(tips)
        for r in engine_tips:
            if r not in combined:
                combined.append(r)
        tips = combined[:9]
    elif not tips:
        tips = engine_tips

    # Step 6 — Recurring symptom upgrade
    symptom_summary = ", ".join(matched_symptoms) if matched_symptoms else user_message[:120]
    if check_recurring(email, symptom_summary) and triage_level == "HOME_CARE":
        triage_level  = "CLINIC_VISIT"
        triage_reason += " — symptoms recurring for multiple days"

    # Step 7 — Save to DB
    save_patient(email, symptom_summary, risk_pct, triage_level)

    # Step 8 — Icons
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
        "symptom_icons": icons[:5],
        "triage_level": triage_level,
        "triage_reason": triage_reason,
        "risk_score": risk_pct,
        "risk_level": risk_label,
        "matched_symptoms": [s.replace("_", " ") for s in matched_symptoms],
        "home_care_tips": tips,
        "warning_signs": warnings,
        "follow_up": follow_up,
        "followup_options": followup_opts
    })


@app.route("/", methods=["GET"])
def home():
    return send_from_directory(".", "index.html")

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "status": "MediGuide AI backend running",
        "version": "2.0",
        "ml_available": ML_AVAILABLE,
        "ai_enabled": USE_AI_FALLBACK
    })


if __name__ == "__main__":
    print("\n=== MediGuide AI Backend ===")
    print(f"ML Model: {'✅ Loaded' if ML_AVAILABLE else '❌ Not found (rule-based only)'}")
    print(f"Grok AI:   {'✅ Enabled' if USE_AI_FALLBACK else '❌ No API key (set GROK_API_KEY)'}")
    print("Starting server on http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
