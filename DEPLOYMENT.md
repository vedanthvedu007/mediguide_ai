# 🚀 MediGuide AI — Comprehensive Deployment Guide

This guide provides step-by-step instructions for deploying **MediGuide AI** to cloud platforms (such as **Render.com** or **Railway**) with **MongoDB Atlas**, **Google Gemini AI**, and **Gmail SMTP Emergency Alerts**.

---

## 📋 Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Database Setup (MongoDB Atlas)](#2-database-setup-mongodb-atlas)
3. [API Keys & Secrets Setup](#3-api-keys--secrets-setup)
   - [Google Gemini API Key](#a-google-gemini-api-key)
   - [Gmail App Password (Emergency Email Alerts)](#b-gmail-app-password-emergency-email-alerts)
4. [Deployment Option 1: Render.com (Recommended)](#4-deployment-option-1-rendercom-recommended)
5. [Deployment Option 2: Railway.app](#5-deployment-option-2-railwayapp)
6. [Environment Variables Reference](#6-environment-variables-reference)
7. [Post-Deployment Verification Checklist](#7-post-deployment-verification-checklist)
8. [Troubleshooting & FAQ](#8-troubleshooting--faq)

---

## 1. Prerequisites

Before starting deployment, ensure you have:
* A **GitHub account** with the `health-ai` repository pushed.
* A **MongoDB Atlas account** (Free M0 cluster is sufficient).
* A **Google Cloud / AI Studio account** for Gemini API key.
* A **Render.com** (or Railway.app) account.

---

## 2. Database Setup (MongoDB Atlas)

1. Sign in to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. Create a **Free Shared Cluster (M0)**.
3. Under **Database Access**:
   - Create a database user (e.g. `mediguide_user`).
   - Generate a strong password and save it securely.
4. Under **Network Access**:
   - Click **Add IP Address**.
   - Select **Allow Access from Anywhere (`0.0.0.0/0`)** so your cloud backend (Render/Railway) can connect.
5. Click **Connect** → **Drivers** → Copy the connection string:
   ```text
   mongodb+srv://mediguide_user:<password>@cluster0.xxxxx.mongodb.net/mediguide?retryWrites=true&w=majority
   ```
   *(Replace `<password>` with your actual database user password).*

---

## 3. API Keys & Secrets Setup

### A. Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/apikey).
2. Click **Create API Key**.
3. Copy your key (starts with `AIza...`).

### B. Gmail App Password (Emergency Email Alerts)
1. Go to your [Google Account Settings](https://myaccount.google.com/).
2. Enable **2-Step Verification** under Security.
3. Go to [Google App Passwords](https://myaccount.google.com/apppasswords).
4. Create a new App Password named `MediGuide Alert`.
5. Copy the 16-character password generated.

---

## 4. Deployment Option 1: Render.com (Recommended)

MediGuide AI includes a preconfigured `render.yaml` Blueprint set to **Render's 100% Free Tier** (`plan: free`).

> [!NOTE]
> **Render Free Tier Details**:
> - **Cost**: 100% Free ($0/month, no credit card required).
> - **Specs**: 512 MB RAM, 0.1 CPU, 750 free instance hours per month.
> - **Sleep behavior**: Free services spin down (go to sleep) after 15 minutes of inactivity. When a user opens the URL, it takes ~30-50 seconds to start back up ("cold start").

### Automatic Blueprint Deployment (Easiest & Free)
1. Log in to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** → **Blueprint**.
3. Connect your GitHub repository (`vedanthvedu007/mediguide_ai`).
4. Render will automatically detect `render.yaml` and select the **Free Plan**.
5. Fill in the prompt for environment variables:
   - `MONGO_URI`: Your MongoDB Atlas connection string.
   - `GEMINI_API_KEY`: Your Gemini API key.
   - `SMTP_EMAIL`: Your Gmail address for sending emergency alerts.
   - `SMTP_PASSWORD`: Your 16-character Gmail App Password.
6. Click **Apply**. Render will build and deploy the web service automatically on the Free Tier.

### Manual Web Service Creation (Alternative)
If you prefer configuring the Web Service manually on Render:
1. Click **New +** → **Web Service**.
2. Connect your repository.
3. Configure the settings:
   - **Name**: `mediguide-ai`
   - **Environment**: `Python 3`
   - **Region**: Select closest to your users (e.g. Singapore / Frankfurt / US East).
   - **Branch**: `main`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `gunicorn --chdir backend app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
4. Under **Environment Variables**, add:
   | Key | Value |
   |---|---|
   | `MONGO_URI` | `mongodb+srv://...` |
   | `SECRET_KEY` | *(Click "Generate" or type a random string)* |
   | `GEMINI_API_KEY` | `AIza...` |
   | `BLOOD_BANK_EMAIL` | `bloodbank@hospital.com` |
   | `BLOOD_BANK_PHONE` | `+91-6364147711` |
   | `SMTP_EMAIL` | `your-email@gmail.com` |
   | `SMTP_PASSWORD` | `xxxx xxxx xxxx xxxx` |
   | `FLASK_ENV` | `production` |
5. Click **Create Web Service**.

---

## 5. Deployment Option 2: Railway.app

1. Log in to [Railway.app](https://railway.app/).
2. Click **New Project** → **Deploy from GitHub repo**.
3. Select `mediguide_ai`.
4. Add Variables in Railway settings matching the table in Section 6.
5. In **Settings** → **Build & Deploy**:
   - **Start Command**: `gunicorn --chdir backend app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
6. Click **Generate Domain** to get your public URL.

---

## 5B. Deployment Option 3: Frontend on Vercel + Backend on Render

Deploying your frontend on **Vercel** gives you **instant initial page loads (0-second cold start)** via Vercel's global CDN, while keeping your Flask ML server on **Render**.

### Step 1: Deploy Backend to Render
Deploy your backend to Render following [Section 4](#4-deployment-option-1-rendercom-recommended).
Copy your live Render backend URL (e.g. `https://mediguide-ai-10gp.onrender.com`).

### Step 2: Set your Render URL on Vercel
You have **2 easy options** to link Vercel to your Render backend:

#### Option A: Using Vercel Environment Variables (Recommended)
1. Go to your project on the [Vercel Dashboard](https://vercel.com).
2. Go to **Settings** → **Environment Variables**.
3. Add a new variable:
   - **Key**: `NEXT_PUBLIC_BACKEND_URL` (or `BACKEND_URL`)
   - **Value**: `https://mediguide-ai-10gp.onrender.com` *(Replace with your actual Render URL)*
   - **Target**: Production, Preview, Development
4. Click **Save**.

#### Option B: Edit `frontend/vercel.json` Proxy Rewrites
Your repo includes a preconfigured [frontend/vercel.json](file:///c:/Users/vedum/Desktop/health-ai/frontend/vercel.json). Open `frontend/vercel.json` and replace `https://mediguide-ai-10gp.onrender.com` with your live Render backend URL. This routes all API calls seamlessly without any CORS issues!

### Step 3: Deploy to Vercel
1. Log in to [Vercel](https://vercel.com).
2. Click **Add New...** → **Project**.
3. Import your GitHub repository (`vedanthvedu007/mediguide_ai`).
4. Set **Root Directory** to `frontend`.
5. Under **Build and Output Settings**:
   - Framework Preset: **Other**
   - Output Directory: `.`
6. Click **Deploy**. Vercel will host your static interface instantly!

---

## 6. Environment Variables Reference

| Variable | Required? | Description | Example / Default |
|---|---|---|---|
| `MONGO_URI` | Yes | MongoDB Atlas connection string | `mongodb+srv://user:pass@cluster.mongodb.net/mediguide` |
| `SECRET_KEY` | Yes | Flask session & cookie encryption secret | Any long random string |
| `GEMINI_API_KEY` | Optional | Google Gemini API Key for enriched advice | `AIzaSy...` (Falls back to offline rules if empty) |
| `BLOOD_BANK_EMAIL` | Yes | Target email recipient for emergency alerts | `bloodbank@hospital.com` |
| `BLOOD_BANK_PHONE` | Yes | Emergency hotline phone number | `+91-6364147711` |
| `SMTP_EMAIL` | Optional | Gmail sender address for alert dispatch | `sender@gmail.com` |
| `SMTP_PASSWORD` | Optional | Gmail 16-character App Password | `abcd efgh ijkl mnop` |
| `FLASK_ENV` | Yes | Environment mode | `production` |
| `PORT` | Auto | Assigned automatically by host | Default `5000` |

---

## 7. Post-Deployment Verification Checklist

After your deployment completes and returns a live URL (e.g. `https://mediguide-ai.onrender.com`):

- [ ] **1. Health Check Endpoint**: Open `https://your-app.onrender.com/` in your browser. Verify it returns the full MediGuide AI user interface.
- [ ] **2. Backend Connectivity**: On the Home panel, check the **ML Server Connection** stat card. It should show `[OK] Online`.
- [ ] **3. User Registration & Auth**: Register a test account or log in with `demo@mediguide.ai` / `health123`.
- [ ] **4. Symptom Triage Check**:
  - Go to **AI Doctor** panel.
  - Type: `"I have fever, cough, and body pain"`.
  - Verify that triage return levels (`HOME_CARE` or `CLINIC_VISIT`) and home remedies render cleanly.
- [ ] **5. Emergency Alert Check**:
  - In AI Doctor chat, type: `"I have severe chest pain, radiating arm pain, and breathlessness"`.
  - Verify that triage triggers `EMERGENCY` level, displays emergency red alert banners, and logs blood bank alerts to MongoDB.
- [ ] **6. History Persistence**: Go to **Report** panel and confirm your symptom check timeline is saved.

---

## 8. Troubleshooting & FAQ

### Q: The backend shows "Offline" in the dashboard.
* **Fix**: Ensure your host environment variable `Accept: application/json` is being processed. The root `/` route serves HTML for web browser navigation and JSON for API status checks.

### Q: MongoDB SSL Handshake / Certificate Verification Failed on Render.
* **Cause**: Cloud Linux containers (like Render) lack default Mozilla Root CA SSL certificates needed by MongoDB Atlas.
* **Fix Applied**: I added `certifi` to `backend/requirements.txt` and configured `mongo.py` to pass `tlsCAFile=certifi.where()` with a automatic fallback.
* **Additional Step**: Check your **MongoDB Atlas Network Access** (`0.0.0.0/0`) and ensure your DB password doesn't contain unencoded special characters like `@` or `#` (if it does, URL-encode `@` as `%40`).

### Q: Gemini AI responses are not showing up.
* **Fix**: Check `GEMINI_API_KEY` in your environment variables. If missing or invalid, MediGuide AI automatically falls back to built-in rule-based remedies so the system remains 100% operational offline.

### Q: Emergency emails are not sending.
* **Fix**: Ensure `SMTP_EMAIL` and `SMTP_PASSWORD` are correctly set. `SMTP_PASSWORD` must be a 16-character **App Password**, not your regular Gmail password.
