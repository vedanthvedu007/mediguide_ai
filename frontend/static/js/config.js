/* ════════════════════════════════════════════════════════════
   MEDIGUIDE AI v3.0 — Global State & Constants
   config.js
════════════════════════════════════════════════════════════ */

const APP_VERSION = '3.0';

// ─── Backend ───────────────────────────────────────────────
let BACKEND_URL    = window.location.origin;
let backendOnline  = false;

// ─── Session State ─────────────────────────────────────────
let currentUser          = null;
let conversationHistory  = [];
let sessionHistory       = [];
let sessionChecks        = 0;
let isSending            = false;
let userRating           = 0;

// ─── BMI / Body ────────────────────────────────────────────
let currentBMI           = null;
let currentBMICategory   = '';
let currentAge           = 25;
let currentSeverityAdjust= 0;

// ─── Body Map ──────────────────────────────────────────────
let selectedBodyRegion   = null;
let selectedSymptoms     = [];
let selectedSeverity     = '';

// ─── Demo Credentials ──────────────────────────────────────
const DEMO = {
  email: 'demo@mediguide.ai',
  pass:  'health123',
  name:  'Demo User',
  age:   28
};

// ─── Body Map Region → Symptom Options ────────────────────
const REGION_SYMPTOMS = {
  head: [
    { id: 'headache',          label: '🤕 Headache' },
    { id: 'dizziness',         label: '😵 Dizziness' },
    { id: 'high fever',        label: '🌡️ High Fever' },
    { id: 'stiff neck',        label: '😬 Stiff Neck' },
    { id: 'blurred vision',    label: '👁️ Blurred Vision' },
    { id: 'runny nose',        label: '🤧 Runny Nose' },
    { id: 'sore throat',       label: '🤒 Sore Throat' },
    { id: 'ear pain',          label: '👂 Ear Pain' }
  ],
  chest: [
    { id: 'chest pain',        label: '💔 Chest Pain' },
    { id: 'breathlessness',    label: '😮 Breathlessness' },
    { id: 'cough',             label: '😮‍💨 Cough' },
    { id: 'palpitations',      label: '💓 Palpitations' },
    { id: 'phlegm',            label: '🫧 Phlegm / Mucus' },
    { id: 'fast heart rate',   label: '💗 Fast Heart Rate' }
  ],
  abdomen: [
    { id: 'stomach pain',      label: '🫃 Stomach Pain' },
    { id: 'nausea',            label: '🤢 Nausea' },
    { id: 'vomiting',          label: '🤮 Vomiting' },
    { id: 'diarrhoea',         label: '🏃 Diarrhoea' },
    { id: 'constipation',      label: '😣 Constipation' },
    { id: 'bloating',          label: '💨 Bloating / Gas' }
  ],
  back: [
    { id: 'lower back pain',   label: '🦴 Lower Back Pain' },
    { id: 'upper back pain',   label: '🦴 Upper Back Pain' },
    { id: 'muscle pain',       label: '💪 Muscle Ache' },
    { id: 'stiffness',         label: '😬 Stiffness' }
  ],
  leftarm: [
    { id: 'arm pain',          label: '💪 Arm Pain' },
    { id: 'weakness in limbs', label: '😔 Weakness' },
    { id: 'joint pain',        label: '🦴 Joint Pain' },
    { id: 'swelling',          label: '🫁 Swelling' }
  ],
  rightarm: [
    { id: 'arm pain',          label: '💪 Arm Pain' },
    { id: 'weakness in limbs', label: '😔 Weakness' },
    { id: 'joint pain',        label: '🦴 Joint Pain' },
    { id: 'swelling',          label: '🫁 Swelling' }
  ],
  legs: [
    { id: 'leg pain',          label: '🦵 Leg Pain' },
    { id: 'knee pain',         label: '🦴 Knee Pain' },
    { id: 'swollen legs',      label: '🦵 Swollen Legs' },
    { id: 'cramps',            label: '😣 Cramps' },
    { id: 'painful walking',   label: '🚶 Painful Walking' }
  ],
  skin: [
    { id: 'skin rash',         label: '🔴 Skin Rash' },
    { id: 'itching',           label: '🤌 Itching' },
    { id: 'yellowing of skin', label: '🟡 Yellow Skin' },
    { id: 'blister',           label: '🫧 Blisters' },
    { id: 'bruising',          label: '🟣 Bruising' }
  ]
};

// ─── Local Remedy Data ──────────────────────────────────────
const REMEDY_DATA = [
  {
    id: 'fever', category: 'fever', icon: '🌡️',
    title: 'Fever / Bukhar',
    steps: [
      '💊 Take Paracetamol 500mg every 6 hours (max 4 doses/day)',
      '💧 Drink 8–10 glasses of water or ORS solution',
      '🧊 Apply damp cool cloth on forehead to reduce temperature',
      '🛌 Rest in cool, ventilated room — wear light clothing',
      '🌿 Tulsi + ginger tea with honey — traditional fever remedy',
      '🌡️ Monitor temp every 4 hours; seek help if above 103°F'
    ],
    escalate: '⚠️ Fever above 103°F (39.4°C) or lasting 3+ days → visit doctor immediately'
  },
  {
    id: 'headache', category: 'pain', icon: '🤕',
    title: 'Headache / Sir Dard',
    steps: [
      '💊 Take Paracetamol 500mg or Ibuprofen 400mg for pain relief',
      '🌑 Rest in a dark, quiet room — light and noise worsen migraines',
      '🧊 Apply cold compress on forehead or warm on back of neck',
      '💧 Drink water — dehydration is the most common headache cause',
      '🌿 Peppermint oil on temples, or ginger tea helps naturally'
    ],
    escalate: '⚠️ Sudden severe "thunderclap" headache → emergency care immediately'
  },
  {
    id: 'cough', category: 'respiratory', icon: '😮‍💨',
    title: 'Cough / Khansi',
    steps: [
      '🍯 1 tsp honey + ginger juice in warm water — soothes dry cough',
      '♨️ Steam inhalation 2–3× daily with eucalyptus oil drops',
      '💊 Benadryl for dry cough or Grilinctus for wet cough (OTC)',
      '🧂 Gargle warm salt water (½ tsp in 1 cup water) 3× daily',
      '🌿 Mulethi (licorice root) in warm water soothes throat'
    ],
    escalate: '⚠️ Coughing blood or lasting 2+ weeks → see a doctor'
  },
  {
    id: 'stomach', category: 'stomach', icon: '🫃',
    title: 'Stomach Pain / Pet Dard',
    steps: [
      '🌿 Ajwain (carom seeds) in warm water reduces stomach cramps',
      '💊 Antacids (Gelusil, Eno) if acidity or heartburn is the cause',
      '🍵 Peppermint or fennel (saunf) tea relieves gas and bloating',
      '🛌 Rest; avoid eating until pain reduces',
      '🚫 Avoid spicy, oily, and heavy foods during stomach pain'
    ],
    escalate: '⚠️ Severe pain with fever or vomiting blood → emergency care'
  },
  {
    id: 'diarrhoea', category: 'stomach', icon: '🏃',
    title: 'Diarrhoea / Dast',
    steps: [
      '💧 Drink ORS (1 packet in 1L water) — replace electrolytes urgently',
      '🍚 BRAT diet: Banana, Rice, Applesauce, Toast — easy to digest',
      '🚫 Avoid milk, coffee, fatty food until stools normalize',
      '💊 Loperamide (Imodium) 2mg — reduces loose motion frequency',
      '🌿 Buttermilk with cumin (jeera) and salt helps recovery'
    ],
    escalate: '⚠️ Blood in stool or lasting 2+ days → visit clinic'
  },
  {
    id: 'vomiting', category: 'stomach', icon: '🤢',
    title: 'Nausea & Vomiting',
    steps: [
      '⏸️ Stop eating for 1–2 hours after vomiting episode',
      '💧 Sip small amounts of ORS or clear liquid every 5–10 minutes',
      '🍚 Eat bland food when tolerated: rice water, khichdi, banana',
      '💊 Domperidone 10mg (Vomikind) for nausea — available OTC',
      '🌿 Ginger tea or ginger candy helps reduce nausea naturally'
    ],
    escalate: '⚠️ Vomiting blood or lasting 24+ hours → see doctor immediately'
  },
  {
    id: 'cold', category: 'respiratory', icon: '🤧',
    title: 'Cold / Nazla Zukam',
    steps: [
      '♨️ Steam inhalation 2–3× daily clears nasal congestion',
      '🍯 Honey + ginger + tulsi tea boosts immunity and soothes throat',
      '💊 Cetirizine 10mg for runny nose and sneezing (OTC)',
      '🧂 Saline nasal drops 2–3 drops each nostril for congestion',
      '🌿 Haldi (turmeric) milk at bedtime fights infection'
    ],
    escalate: '⚠️ Cold with high fever or difficulty breathing → doctor visit'
  },
  {
    id: 'skin_rash', category: 'skin', icon: '🔴',
    title: 'Skin Rash / Chamdi Ki Bimari',
    steps: [
      '🚫 Do NOT scratch — scratching worsens rash and risks infection',
      '🧴 Apply calamine lotion to soothe itching and redness',
      '💊 Cetirizine 10mg antihistamine if rash is itchy',
      '🔍 Identify trigger: new soap, food, fabric, or plant contact',
      '🌿 Aloe vera gel soothes most minor skin rashes effectively'
    ],
    escalate: '⚠️ Rapidly spreading rash, blisters, or associated fever → doctor immediately'
  },
  {
    id: 'back_pain', category: 'pain', icon: '🦴',
    title: 'Back Pain / Kamar Dard',
    steps: [
      '🌡️ Apply warm compress or heating pad on lower back 15–20 min',
      '💊 Ibuprofen 400mg reduces inflammation and back pain',
      '🧘 Gentle knee-to-chest stretch while lying flat helps lower back',
      '🪑 Maintain proper posture — avoid slouching or hunching',
      '🌿 Mustard oil massage on affected area reduces stiffness'
    ],
    escalate: '⚠️ Back pain with leg numbness or bladder control issues → emergency'
  },
  {
    id: 'dizziness', category: 'other', icon: '😵',
    title: 'Dizziness / Chakkar',
    steps: [
      '🪑 Sit or lie down immediately to prevent falls',
      '💧 Drink water or electrolyte drink — dehydration causes dizziness',
      '🍬 Have a small snack if low blood sugar is suspected',
      '🌿 Ginger tea or ginger candy helps reduce dizziness and nausea',
      '🧂 A glass of ORS or nimbu pani (lemon water + salt) helps'
    ],
    escalate: '⚠️ Sudden severe dizziness with chest pain or vision problems → call 108'
  },
  {
    id: 'chest_pain', category: 'emergency', icon: '💔',
    title: 'Chest Pain',
    steps: [
      '🚨 Chest pain can be a medical emergency — do NOT ignore',
      '📞 Call 108 immediately if pain is crushing, squeezing, or radiates to arm/jaw',
      '🪑 Sit upright — do NOT lie flat, stay calm and breathe slowly',
      '🚗 Do NOT drive yourself to hospital — call for help',
      '💊 Chew 1 aspirin (325mg) if heart attack suspected and not allergic'
    ],
    escalate: '🚨 Any chest pain + sweating + arm pain = CALL 108 NOW'
  },
  {
    id: 'body_pain', category: 'pain', icon: '💪',
    title: 'Body Pain / Badan Dard',
    steps: [
      '💊 Ibuprofen 400mg or Paracetamol 500mg for muscle/body ache',
      '🌡️ Apply warm compress or hot water bag on sore muscle areas',
      '🛌 Rest and avoid heavy physical activity until pain reduces',
      '🧘 Light gentle stretching reduces muscle stiffness',
      '🥛 Turmeric milk (haldi doodh) — excellent anti-inflammatory'
    ],
    escalate: '⚠️ Severe body pain with high fever → visit doctor for evaluation'
  }
];

// ─── Ticker Alerts ─────────────────────────────────────────
const HEALTH_TICKERS = [
  '🌡️ Monsoon season: Watch for dengue, malaria & leptospirosis',
  '💧 Stay hydrated: Drink 8–10 glasses of water daily',
  '🧼 Wash hands before meals to prevent 80% of common infections',
  '🚑 Emergency Ambulance: Call 108 — Free & Available 24/7',
  '🩸 Blood required? Call Blood Bank: 1097 — Free blood helpline',
  '🌿 Tulsi, ginger & haldi: Nature\'s immunity boosters',
  '💊 Do not self-medicate for antibiotics — always consult a doctor',
  '📍 Nearest PHC or CHC: Visit for free government healthcare',
  '🍚 Oral Rehydration Solution (ORS): Best remedy for diarrhoea',
  '🚨 Stroke signs: Face drooping, Arm weak, Speech slurred → 108!'
];

// ─── API Helper ─────────────────────────────────────────────
async function apiCall(endpoint, method = 'GET', body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(BACKEND_URL + endpoint, opts);

  // For 4xx responses, try to parse the JSON body so callers can
  // read status fields like "exists" or "error" and show proper messages.
  if (!res.ok) {
    if (res.status >= 400 && res.status < 500) {
      try {
        return await res.json();
      } catch (_) {
        // If body isn't valid JSON, fall through to throw
      }
    }
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
}

// ─── Toast Notifications ────────────────────────────────────
function showToast(msg, type = 'info', duration = 3000) {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const icons = { info: 'ℹ️', success: '✅', warn: '⚠️', danger: '🚨' };
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `<span>${icons[type] || ''}</span><span>${msg}</span>`;
  container.appendChild(el);
  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transform = 'translateX(20px)';
    el.style.transition = 'all 0.3s';
    setTimeout(() => el.remove(), 300);
  }, duration);
}
