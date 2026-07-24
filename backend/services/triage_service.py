import numpy as np
from config import ML_AVAILABLE, model, encoder, FEATURES

# ── Kannada symptom keyword mappings (transliterated + script) ──
KANNADA_KEYWORDS = {
    "mild_fever":      ["jwara", "jvara", "jwara ide", "jvara ide", "ಜ್ವರ", "bukhar"],
    "high_fever":      ["jaasti jwara", "severe jwara", "tumbaa jwara", "ಹೆಚ್ಚು ಜ್ವರ"],
    "headache":        ["tale novu", "tale dukha", "talenu", "ಮಾಥೆ ನೋವು", "ತಲೆನೋವು", "sir dard"],
    "cough":           ["kemmu", "ಕೆಮ್ಮು", "khansi", "khansi ide"],
    "chest_pain":      ["edhe novu", "ಎದೆ ನೋವು", "edege novu", "edhe dukha"],
    "breathlessness":  ["usiraata", "ಉಸಿರಾಟ", "usirata", "usiraata kashta", "ushvasa"],
    "vomiting":        ["vomit aagide", "vanthiaagthaida", "ಓಕರಿಕೆ", "okarike"],
    "diarrhoea":       ["bathti", "loose motion", "ಬಿಡುಹಲ್ಲು", "biduhullu", "beedi"],
    "stomach_pain":    ["hotte novu", "ಹೊಟ್ಟೆ ನೋವು", "hotte dukha", "pet novu"],
    "nausea":          ["waak anta ide", "sikku", "ಓಕರಿ"],
    "dizziness":       ["tale tirugutte", "tale tiru", "ತಲೆ ತಿರುಗು", "chakkar", "gidugiddu"],
    "fatigue":         ["dappa", "omme aagtilla", "ಆಯಾಸ", "aayasa", "sakthi illa"],
    "joint_pain":      ["mari novu", "ಮರಿ ನೋವು", "sandhiya novu", "joint novu"],
    "back_pain":       ["beenu novu", "ಬೆನ್ನು ನೋವು", "beennu novu", "kamar novu"],
    "skin_rash":       ["chamadi rash", "ಚರ್ಮ ದದ್ದು", "charma daddu", "chamadi kizhi"],
    "itching":         ["turike", "ತುರಿಕೆ", "turikke", "chamadi turike"],
    "muscle_pain":     ["snaayu novu", "ಸ್ನಾಯು ನೋವು", "maamsa novu", "badan novu"],
    "throat_irritation": ["gantalu novu", "ಗಂಟಲು ನೋವು", "gantalu", "gala novu"],
    "runny_nose":      ["mookku seeri", "ಮೂಗು ಸೋರು", "nasal drip kannada"],
    "shivering":       ["nadedukoLLutide", "ಚಳಿ", "chali", "titiputhide"],
    "coma":            ["prajna illa", "ಪ್ರಜ್ಞೆ ಇಲ್ಲ", "unconscious", "pragna illa"],
}

SYMPTOM_KEYWORDS = {
    "itching":                      ["itch", "itching", "itchy"] + KANNADA_KEYWORDS.get("itching", []),
    "skin_rash":                    ["rash", "skin rash", "skin eruption", "red skin"] + KANNADA_KEYWORDS.get("skin_rash", []),

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
    "cough":                        ["cough", "coughing", "dry cough", "wet cough"] + KANNADA_KEYWORDS.get("cough", []),
    "high_fever":                   ["high fever", "very high fever", "severe fever", "104", "103"] + KANNADA_KEYWORDS.get("high_fever", []),
    "sunken_eyes":                  ["sunken eyes", "hollow eyes"],
    "breathlessness":               ["breathless", "shortness of breath", "cannot breathe",
                                     "difficulty breathing", "breathing problem", "no breath"] + KANNADA_KEYWORDS.get("breathlessness", []),
    "sweating":                     ["sweat", "sweating", "night sweat", "excessive sweating"],
    "dehydration":                  ["dehydrated", "dehydration", "dry mouth", "very thirsty"],
    "indigestion":                  ["indigestion", "digestion problem"],
    "headache":                     ["headache", "head pain", "head hurts", "migraine",
                                     "head ache", "head throbbing"] + KANNADA_KEYWORDS.get("headache", []),
    "yellowish_skin":               ["yellow skin", "yellowish skin", "jaundice skin"],
    "dark_urine":                   ["dark urine", "brown urine", "dark pee"],
    "nausea":                       ["nausea", "nauseated", "feeling sick", "queasy", "want to vomit"] + KANNADA_KEYWORDS.get("nausea", []),
    "loss_of_appetite":             ["no appetite", "loss of appetite", "not eating", "no hunger"],
    "pain_behind_the_eyes":         ["eye pain", "pain behind eyes", "eyes hurt"],
    "back_pain":                    ["back pain", "backache", "lower back pain", "back hurts"] + KANNADA_KEYWORDS.get("back_pain", []),
    "constipation":                 ["constipation", "constipated", "hard stool", "no bowel movement"],
    "abdominal_pain":               ["abdominal pain", "abdomen pain", "belly pain", "gut pain"],
    "diarrhoea":                    ["diarrhea", "diarrhoea", "loose motion", "loose stool",
                                     "watery stool", "runny stool"] + KANNADA_KEYWORDS.get("diarrhoea", []),
    "mild_fever":                   ["mild fever", "low grade fever", "slight fever", "fever", "temperature"] + KANNADA_KEYWORDS.get("mild_fever", []),
    "yellow_urine":                 ["yellow urine", "dark yellow urine"],
    "yellowing_of_eyes":            ["yellow eyes", "jaundice eyes", "eyes turning yellow"],
    "acute_liver_failure":          ["liver failure", "liver problem"],
    "fluid_overload":               ["fluid retention", "water retention"],
    "swelling_of_stomach":          ["stomach swelling", "bloated stomach", "belly swollen"],
    "swelled_lymph_nodes":          ["swollen lymph node", "swollen gland", "lymph node"],
    "malaise":                      ["malaise", "generally unwell", "feeling unwell", "not feeling well"],
    "blurred_and_distorted_vision": ["blurred vision", "blurry vision", "vision problem", "double vision"],
    "phlegm":                       ["phlegm", "mucus", "sputum", "thick mucus"],
    "throat_irritation":            ["throat irritation", "scratchy throat", "sore throat", "throat pain"] + KANNADA_KEYWORDS.get("throat_irritation", []),
    "redness_of_eyes":              ["red eyes", "pink eye", "eye redness"],
    "sinus_pressure":               ["sinus", "sinus pressure", "sinusitis"],
    "runny_nose":                   ["runny nose", "nose running", "nasal drip"] + KANNADA_KEYWORDS.get("runny_nose", []),
    "congestion":                   ["congestion", "stuffy nose", "blocked nose"],
    "chest_pain":                   ["chest pain", "chest tight", "chest pressure", "chest hurts",
                                     "heart pain", "chest ache", "chest discomfort"] + KANNADA_KEYWORDS.get("chest_pain", []),
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

KANNADA_REMEDIES = {
    "fever": [
        "💊 6 ಗಂಟೆಗೊಮ್ಮೆ ಪ್ಯಾರಾಸಿಟಮಾಲ್ 500mg ತೆಗೆದುಕೊಳ್ಳಿ (ದಿನಕ್ಕೆ ಗರಿಷ್ಠ 4 ಡೋಸ್)",
        "💧 ನಿರ್ಜಲೀಕರಣ ತಡೆಯಲು 8-10 ಲೋಟ ನೀರು ಅಥವಾ ORS ಕುಡಿಯಿರಿ",
        "🧊 ಜ್ವರ ಕಡಿಮೆ ಮಾಡಲು ಹಣೆಗೆ ತಣ್ಣನೆಯ ಒದ್ದೆ ಬಟ್ಟೆ ಹಾಕಿ",
        "🛌 ತಂಪಾದ, ಗಾಳಿಯಾಡುವ ಕೋಣೆಯಲ್ಲಿ ವಿಶ್ರಾಂತಿ ಪಡೆಯಿರಿ — ಹಗುರವಾದ ಬಟ್ಟೆ ಧರಿಸಿ",
        "🌿 ತುಳಸಿ + ಶುಂಟಿ ಟೀ ಜೊತೆಗೆ ಜೇನುತುಪ್ಪ — ನೈಸರ್ಗಿಕ ಜ್ವರದ ಮನೆಮದ್ದು",
        "⚠️ ಜ್ವರ 103°F ಗಿಂತ ಹೆಚ್ಚಿದ್ದರೆ ಅಥವಾ 3 ದಿನಗಳಿಗಿಂತ ಹೆಚ್ಚು ಇದ್ದರೆ ತಕ್ಷಣ ವೈದ್ಯರನ್ನು ಭೇಟಿ ಮಾಡಿ"
    ],
    "headache": [
        "💊 ನೋವು ಶಮನಕ್ಕೆ ಪ್ಯಾರಾಸಿಟಮಾಲ್ 500mg ತೆಗೆದುಕೊಳ್ಳಿ",
        "🌑 ಕತ್ತಲಾದ, ಪ್ರಶಾಂತವಾದ ಕೋಣೆಯಲ್ಲಿ ವಿಶ್ರಾಂತಿ ಪಡೆಯಿರಿ",
        "💧 ಚೆನ್ನಾಗಿ ನೀರು ಕುಡಿಯಿರಿ — ನಿರ್ಜಲೀಕರಣ ತಲೆನೋವಿಗೆ ಮುಖ್ಯ ಕಾರಣ",
        "🌿 ಶುಂಟಿ ಟೀ ಅಥವಾ ತುಳಸಿ ಕಷಾಯ ನೈಸರ್ಗಿಕವಾಗಿ ಶಮನ ನೀಡುತ್ತದೆ",
        "⚠️ ದಿಢೀರ್ ತೀವ್ರ ತಲೆನೋವು ಬಂದರೆ ತಕ್ಷಣ ವೈದ್ಯರನ್ನು ಭೇಟಿ ಮಾಡಿ"
    ],
    "cough": [
        "🍯 1 ಚಮಚ ಜೇನುತುಪ್ಪ + ಶುಂಟಿ ರಸ ಬೆಚ್ಚಗಿನ ನೀರಿನಲ್ಲಿ ಕುಡಿಯಿರಿ",
        "♨️ ಬಿಸಿ ನೀರಿನ ಹಾವಿ (Steam) ದಿನಕ್ಕೆ 2-3 ಬಾರಿ ತೆಗೆದುಕೊಳ್ಳಿ",
        "🧂 ಬೆಚ್ಚಗಿನ ಉಪ್ಪು ನೀರಿನಿಂದ ಗಂಟಲು ಕೊಕ್ಕರಿಸಿರಿ (Gargle)",
        "❄️ ತಣ್ಣನೆಯ ಪಾನೀಯಗಳು ಮತ್ತು ಐಸ್‌ಕ್ರೀಮ್ ತಪ್ಪಿಸಿ",
        "⚠️ ಕೆಮ್ಮಿನಲ್ಲಿ ರಕ್ತ ಬಂದರೆ ತಕ್ಷಣ ಆಸ್ಪತ್ರೆಗೆ ಭೇಟಿ ನೀಡಿ"
    ],
    "chest_pain": [
        "🚨 ಎದೆ ನೋವು ತುರ್ತು ಪರಿಸ್ಥಿತಿಯಾಗಿರಬಹುದು — ತಡ ಮಾಡಬೇಡಿ",
        "📞 ಎದೆ ನೋವು ತೀವ್ರವಾಗಿದ್ದರೆ ತಕ್ಷಣ 108 ಗೆ ಕರೆ ಮಾಡಿ",
        "🪑 ನೆಟ್ಟಗೆ ಕುಳಿತುಕೊಳ್ಳಿ — ಮಲಗಬೇಡಿ, ಶಾಂತರಾಗಿರಿ",
        "🚗 ನೀವೇ ಕಾರು/ಬೈಕ್ ಓಡಿಸಬೇಡಿ — ತಕ್ಷಣ ಸಹಾಯ ಪಡೆಯಿರಿ"
    ],
    "breathlessness": [
        "🚨 ಉಸಿರಾಟದ ತೊಂದರೆ ಇದ್ದರೆ ತಕ್ಷಣ 108 ಆಂಬ್ಯುಲೆನ್ಸ್‌ಗೆ ಕರೆ ಮಾಡಿ",
        "🪑 ನೆಟ್ಟಗೆ ಕುಳಿತುಕೊಳ್ಳಿ, ತಾಜಾ ಗಾಳಿ ಇರುವ ಕಡೆ ಇರಿ",
        "💨 ಆಸ್ತಮಾ ಇದ್ದರೆ ನಿಮ್ಮ ಇನ್ಹೇಲರ್ ಬಳಸಿ"
    ],
    "vomiting": [
        "💧 ORS ನೀರನ್ನು ಸಣ್ಣ ಸಣ್ಣ ಪ್ರಮಾಣದಲ್ಲಿ ಕುಡಿಯಿರಿ",
        "🍚 ಹಗುರವಾದ ಆಹಾರ ಸೇವಿಸಿ: ಗಂಜಿ ನೀರು, ಮಜ್ಜಿಗೆ, ಬಾಳೆಹಣ್ಣು",
        "🌿 ಶುಂಟಿ ಟೀ ಕಷಾಯ ವಾಂತಿ ಭಾವನೆ ಕಡಿಮೆ ಮಾಡುತ್ತದೆ"
    ],
    "diarrhoea": [
        "💧 ORS (1 ಲೀಟರ್ ನೀರಿನಲ್ಲಿ 1 ಪ್ಯಾಕೆಟ್) ತಕ್ಷಣ ಕುಡಿಯಿರಿ",
        "🍚 ಮಜ್ಜಿಗೆ ಅನ್ನ, ಗಂಜಿ ನೀರು, ಬಾಳೆಹಣ್ಣು ಸೇವಿಸಿ",
        "🚫 ಹಾಲು ಮತ್ತು ಮಸಾಲೆ ಪದಾರ್ಥಗಳನ್ನು ತಪ್ಪಿಸಿ"
    ],
    "body_pain": [
        "💊 ನೋವು ಶಮನಕ್ಕೆ ಪ್ಯಾರಾಸಿಟಮಾಲ್ ತೆಗೆದುಕೊಳ್ಳಿ",
        "🌡️ Apply warm compress or hot water bag on sore muscle areas",
        "🛌 Rest and avoid heavy physical activity until pain reduces",
        "🥛 ಅರಿಶಿನ ಹಾಲು ನೈಸರ್ಗಿಕ ಶಮನ ನೀಡುತ್ತದೆ"
    ],
    "general": [
        "🛌 ಚೆನ್ನಾಗಿ ವಿಶ್ರಾಂತಿ ಪಡೆಯಿರಿ (7-8 ಗಂಟೆ ನಿದ್ರೆ)",
        "💧 ದಿನಕ್ಕೆ 8-10 ಲೋಟ ನೀರು ಕುಡಿಯಿರಿ",
        "🥗 ಹಗುರವಾದ, ಪೌಷ್ಟಿಕ ಆಹಾರ ಸೇವಿಸಿ",
        "⚠️ ರೋಗಲಕ್ಷಣ ಹೆಚ್ಚಾದರೆ ತಕ್ಷಣ ಹತ್ತಿರದ ಪಿಹೆಚ್‌ಸಿ/ವೈದ್ಯರನ್ನು ಭೇಟಿ ಮಾಡಿ"
    ]
}

def pick_remedies(matched: list, risk_label: str, raw_text: str = "") -> list:
    if risk_label == "HIGH":
        return EMERGENCY_TIPS

    raw_low = raw_text.lower()
    is_kannada = any(k in raw_low for k in ["jwara", "jvara", "ಜ್ವರ", "kemmu", "ಕೆಮ್ಮು", "novu", "ನೋವು", "hotte", "edhe", "usir", "turike", "aayasa", "dappa", "gantalu"])
    active_remedies = KANNADA_REMEDIES if is_kannada else REMEDIES

    sym_map = {
        "high_fever": "fever", "mild_fever": "fever",
        "headache": "headache",
        "cough": "cough", "phlegm": "cough",
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
            tips.extend(active_remedies.get(category, []))
    if not tips:
        tips = active_remedies["general"]
    return tips[:8]

WARNING_SIGNS = {
    "fever": [
        "Fever rises above 103°F (39.4°C) or lasts more than 3 days",
        "Stiff neck, severe headache, or confusion",
        "Difficulty breathing or rapid heart rate"
    ],
    "cough": [
        "Coughing up blood or dark phlegm",
        "Shortness of breath or chest pain when coughing",
        "Fever remains high for multiple days"
    ],
    "chest_pain": [
        "Pain radiating to your arm, neck, jaw, or back",
        "Shortness of breath, sweating, dizziness, or nausea",
        "Feeling of pressure, tightness, or squeezing in your chest"
    ],
    "breathlessness": [
        "Inability to speak in full sentences without pausing",
        "Blue lips or face, or chest pulling in while breathing",
        "Confusion, disorientation, or feeling faint"
    ],
    "vomiting": [
        "Unable to keep any liquids down for more than 24 hours",
        "Signs of severe dehydration (dry mouth, no urine for 8 hours)",
        "Vomiting blood or dark green bile"
    ],
    "diarrhoea": [
        "Extreme weakness, dizziness, or fainting",
        "Blood in stool or black sticky stools",
        "Severe sharp stomach pain or high fever"
    ],
    "skin_rash": [
        "Rash is spreading very rapidly across the body",
        "Formation of painful blisters or open sores",
        "Accompanied by high fever or swollen joints"
    ],
    "sore_throat": [
        "Inability to swallow liquids or open mouth fully",
        "Drooling or difficulty breathing",
        "White patches on your throat or tonsils"
    ],
    "stomach_pain": [
        "Severe, sudden, or sharp stomach pain",
        "Stomach is very hard or tender to touch",
        "Vomiting blood or having black/bloody stools"
    ],
    "back_pain": [
        "Numbness or weakness in legs or groin area",
        "Loss of bowel or bladder control",
        "Accompanied by unexplained fever or weight loss"
    ],
    "dizziness": [
        "Sudden numbness, weakness, or slurred speech",
        "Loss of balance or difficulty walking",
        "Dizziness accompanied by chest pain or heart racing"
    ],
    "general": [
        "Symptoms suddenly get much worse",
        "Fever rises above 102°F (38.9°C)",
        "New symptoms like chest pain or breathlessness appear",
        "Cannot eat or drink for more than 12 hours"
    ]
}

def pick_warnings(matched: list, risk_label: str) -> list:
    if risk_label == "HIGH":
        return [
            "Difficulty breathing or chest tightness",
            "Chest pain or pressure radiating to arm/jaw",
            "Loss of consciousness or confusion",
            "Severe bleeding that won't stop",
            "Sudden weakness on one side of the body"
        ]
    sym_map = {
        "high_fever": "fever", "mild_fever": "fever",
        "headache": "dizziness",
        "cough": "cough", "phlegm": "cough",
        "chest_pain": "chest_pain",
        "breathlessness": "breathlessness",
        "vomiting": "vomiting", "nausea": "vomiting",
        "diarrhoea": "diarrhoea",
        "muscle_pain": "general", "joint_pain": "general",
        "skin_rash": "skin_rash", "itching": "skin_rash",
        "throat_irritation": "sore_throat",
        "stomach_pain": "stomach_pain", "abdominal_pain": "stomach_pain",
        "back_pain": "back_pain",
        "dizziness": "dizziness",
    }
    seen = set()
    warnings = []
    for sym in matched:
        category = sym_map.get(sym)
        if category and category not in seen:
            seen.add(category)
            warnings.extend(WARNING_SIGNS.get(category, []))
    if not warnings:
        warnings = WARNING_SIGNS["general"]
    return warnings[:6]

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
        "should", "can", "i have", "i am", "my", "bmi", "weight", "height",
        "bukhar", "sir dard", "khansi", "dard", "badan", "pet", "chakkar",
        "jwara", "jvara", "novu", "kemmu", "edhe", "hotte", "tale", "beenu",
        "usirata", "usiraata", "turike", "okarike", "aayasa", "dappa", "gantalu",
        "ನೋವು", "ಜ್ವರ", "ಕೆಮ್ಮು", "ಎದೆ", "ತಲೆ", "ಹೊಟ್ಟೆ", "ತುರಿಕೆ", "ಉಸಿರಾಟ",
    ]
    text_low = text.lower()
    return any(kw in text_low for kw in health_keywords)

def rule_based_response(matched: list, risk_score: int, raw_text: str = "") -> dict:
    raw_lower = raw_text.lower().strip()
    is_kannada = any(k in raw_lower for k in ["jwara", "jvara", "ಜ್ವರ", "kemmu", "ಕೆಮ್ಮು", "novu", "ನೋವು", "hotte", "edhe", "usir", "turike", "aayasa", "dappa", "gantalu"])

    sym_names = [s.replace("_", " ").title() for s in matched[:4]] if matched else []
    sym_phrase = ", ".join(sym_names) if sym_names else "your symptoms"

    is_explicit_emergency = "emergency blood" in raw_lower or "manual blood alert" in raw_lower or "blood required urgent" in raw_lower

    if risk_score >= 70:
        if is_kannada:
            explanation = (
                f"🚨 ನಿಮ್ಮ ರೋಗಲಕ್ಷಣಗಳು ({sym_phrase}) ತೀವ್ರವಾಗಿರುವಂತೆ ಕಾಣಿಸುತ್ತಿವೆ. "
                "ದಯವಿಟ್ಟು ತಕ್ಷಣ ವೈದ್ಯಕೀಯ ಚಿಕಿತ್ಸೆ ಪಡೆಯಿರಿ. ತಡಮಾಡಬೇಡಿ — "
                "ಉಚಿತ ಆಂಬ್ಯುಲೆನ್ಸ್‌ಗಾಗಿ ತಕ್ಷಣ 108 ಗೆ ಕರೆ ಮಾಡಿ!"
            )
        else:
            explanation = (
                f"🚨 Your reported symptoms ({sym_phrase}) indicate a potentially serious condition. "
                "Please seek emergency medical attention immediately. Do not wait — "
                "call 108 for a free ambulance right away!"
            )
        return {
            "simple_explanation": explanation,
            "triage_level": "EMERGENCY",
            "triage_reason": "High-risk symptoms detected — immediate medical attention needed",
            "home_care_tips": EMERGENCY_TIPS,
            "warning_signs": pick_warnings(matched, "HIGH"),
            "follow_up": "ನಿಮಗೆ ಎದೆ ನೋವು ಅಥವಾ ಉಸಿರಾಟದ ತೊಂದರೆ ಇದೆಯೇ?",
            "followup_options": ["ಹೌದು, ಎದೆ ನೋವು", "ಉಸಿರಾಟದ ತೊಂದರೆ", "ತಲೆ ಸುತ್ತು", "ಇಲ್ಲ"]
        }

    elif risk_score >= 40:
        if is_kannada:
            explanation = (
                f"⚠️ ನಿಮಗೆ {sym_phrase} ಲಕ್ಷಣಗಳು ಕಾಣಿಸಿಕೊಂಡಿವೆ. ಇವುಗಳಿಗೆ ವೈದ್ಯರ ಸಲಹೆ ಅಗತ್ಯವಿದೆ. "
                "ದಯವಿಟ್ಟು ಶೀಘ್ರದಲ್ಲೇ ಹತ್ತಿರದ ಕ್ಲಿನಿಕ್ ಅಥವಾ ವೈದ್ಯರನ್ನು ಭೇಟಿ ಮಾಡಿ."
            )
        else:
            explanation = (
                f"⚠️ You are experiencing {sym_phrase}. These are moderate symptoms that need medical evaluation. "
                "Please visit a clinic or doctor soon."
            )
        return {
            "simple_explanation": explanation,
            "triage_level": "CLINIC_VISIT",
            "triage_reason": "Moderate symptoms detected — professional evaluation recommended",
            "home_care_tips": pick_remedies(matched, "MEDIUM", raw_text),
            "warning_signs": pick_warnings(matched, "MEDIUM"),
            "follow_up": "ಈ ರೋಗಲಕ್ಷಣಗಳು ಎಷ್ಟು ದಿನಗಳಿಂದ ಇವೆ?",
            "followup_options": ["ಇಂದಿನಿಂದ", "2-3 ದಿನಗಳು", "3 ದಿನಗಳಿಗಿಂತ ಹೆಚ್ಚು", "ಬಂದು ಹೋಗುತ್ತಿದೆ"]
        }

    else:
        if is_kannada:
            explanation = (
                f"😊 ನಿಮಗೆ {sym_phrase} ಕಾಣಿಸಿಕೊಂಡಿದೆ. ಇವು ಸಾಧಾರಣ ರೋಗಲಕ್ಷಣಗಳಾಗಿದ್ದು, "
                "ಮನೆಯಲ್ಲಿಯೇ ವಿಶ್ರಾಂತಿ ಮತ್ತು ಮನೆಮದ್ದುಗಳ ಮೂಲಕ ಶಮನಗೊಳಿಸಬಹುದು."
            )
        else:
            explanation = (
                f"😊 You are experiencing {sym_phrase}. These appear to be mild symptoms that you can "
                "manage at home with rest and home remedies."
            )
        return {
            "simple_explanation": explanation,
            "triage_level": "HOME_CARE",
            "triage_reason": "Mild symptoms — home care is sufficient",
            "home_care_tips": pick_remedies(matched, "LOW", raw_text),
            "warning_signs": pick_warnings(matched, "LOW"),
            "follow_up": "ನಿಮಗೆ ಯಾವುದೇ ಇತರ ತೊಂದರೆ ಇದೆಯೇ?",
            "followup_options": ["ಜ್ವರ", "ತಲೆನೋವು", "ಅಂಗಾಂಗ ನೋವು", "ಇಲ್ಲ"]
        }



