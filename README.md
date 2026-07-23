# 🩺 MediGuide AI — Rural Healthcare Triage & Remedy Companion

MediGuide AI is a premium, ML-powered healthcare companion designed for rural communities. It offers instant symptom triage, home remedies (including traditional Indian remedies), and automatic emergency warnings for life-threatening conditions.

This project is built using a modern **Flask** backend structured with models and blueprints, a **MongoDB** Atlas database, and a highly responsive, modern single-page vanilla **HTML/CSS/JS** frontend.

---

## 📂 Project Repository Layout

The codebase is structured to keep concerns separate, modular, and professional:

```
health-ai/
├── backend/
│   ├── app.py                        # Flask main application entry point & blueprint registration
│   ├── config.py                     # App configuration (loads environment variables & ML models)
│   ├── requirements.txt              # Project dependencies (pymongo, dnspython, werkzeug, etc.)
│   │
│   ├── db/
│   │   └── mongo.py                  # MongoDB Atlas connection singleton & index enforcement
│   │
│   ├── models/
│   │   ├── user_model.py             # User CRUD, password hashing, and demo user seeding
│   │   ├── patient_model.py          # Patient check-up history & recurrence checking logic
│   │   ├── alert_model.py            # Emergency blood bank alerts saving
│   │   └── feedback_model.py         # User feedback submissions logging
│   │
│   ├── blueprints/
│   │   ├── auth.py                   # Authentication API endpoints (/login, /register)
│   │   └── api.py                    # Symptom triage (/predict), history, alerts, and remedies
│   │
│   ├── services/
│   │   ├── ai_service.py             # Gemini (Google AI) API client for deep health answers (fallback)
│   │   └── triage_service.py         # Symptom keyword extractor and rule-based fallback logic
│   │
│   └── ml_models/                    # Structured folder for ML artifacts
│       ├── model.pkl                 # Pre-trained Random Forest model
│       ├── encoder.pkl               # Target label encoder
│       └── features.pkl              # Symptom features list
│
├── frontend/
│   ├── templates/
│   │   ├── base.html                 # Base Jinja2 layout (includes head tags, metadata, global styles/scripts)
│   │   └── index.html                # Single Page Application frontend layout
│   │
│   └── static/
│       ├── css/                      # Modular style sheets (variables, components, panels, chat, auth, dashboard)
│       └── js/                       # Modular scripts (app, auth, chat, bmi, bodymap, remedies, emergency, report)
│
├── docs/                             # Project documentation and slides
│   └── MediGuide_AI_Hackathon.pptx   # Hackathon presentation slide deck
│
├── .gitignore
├── .env.example
└── render.yaml                       # Production deployment config for Render.com
```

---

## ⚡ Key Features

1. **Intelligent Symptom Triage**: Uses an offline Machine Learning model (`Random Forest`) to predict risk level (`LOW`/`MEDIUM`/`HIGH`) and triage category (`HOME_CARE`/`CLINIC_VISIT`/`EMERGENCY`).
2. **Indian Home Remedies (Rule-based Fallback)**: Suggests effective herbal and home remedies (e.g. Tulsi tea, Haldi milk, Ginger, Ajwain) for mild symptoms.
3. **Gemini AI Integration**: If configured, uses Google's `gemini-2.0-flash-lite` LLM to generate rich, compassionate triage guidelines and warning signs.
4. **Blood Bank Alerts**: Instantly triggers alerts in case of emergency symptoms (e.g. chest pain + breathlessness) and logs them in MongoDB.
5. **Interactive Body Map**: Click on body regions (Head, Chest, Abdomen, Skin, Joints) to auto-fill symptom text.
6. **BMI Risk Calculator**: Dynamically adjusts severity scores and triage response if patient has underlying high-risk BMI ranges.
7. **Patient Check History**: Saves patient checkups in MongoDB and alerts the user if symptoms recur within 48 hours.
8. **Export PDF Report**: Easily compiles the diagnostic details, home care instructions, and emergency alerts into a downloadable PDF printout.

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10+
- MongoDB Atlas cluster (free tier works perfectly)

### 1. Clone & Set Up Directory
Open your terminal inside the `health-ai` project directory:
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows (Command Prompt):
venv\Scripts\activate
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root folder by copying the template:
```bash
copy .env.example .env
```
Open `.env` and configure your settings:
```ini
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/mediguide
SECRET_KEY=your-secure-random-key-here
GEMINI_API_KEY=your-gemini-api-key       # Optional (falls back to offline rule-based if empty)
BLOOD_BANK_EMAIL=bloodbank@hospital.com
BLOOD_BANK_PHONE=+91-XXXXXXXXXX
FLASK_ENV=development
```

---

## 🚀 Running the App locally

Start the Flask application:
```bash
python backend/app.py
```

- Access the frontend dashboard at: **`http://localhost:5000`**
- The app will automatically seed a default demo account on startup:
  - **Email**: `demo@mediguide.ai`
  - **Password**: `health123`

---

## ☁️ Deployment

This project is fully ready for deployment on **Render.com** or any platform supporting a declarative pipeline:

1. Push this repository to GitHub/GitLab.
2. Link the repository to your Render dashboard.
3. Render will automatically parse the `render.yaml` file to provision the service with Gunicorn configured to change directories via `--chdir backend` and run `app:app`.
4. Be sure to configure the environment variable values (`MONGO_URI`, `GEMINI_API_KEY`, etc.) in the Render dashboard's Environment section.
