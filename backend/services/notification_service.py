"""
services/notification_service.py — Blood Bank Email Notifications
=================================================================
Sends a plain Gmail email to BLOOD_BANK_EMAIL when an emergency
is detected.  Uses Python's built-in smtplib — no extra packages needed.

Setup (in .env):
  SMTP_EMAIL    = your_gmail@gmail.com
  SMTP_PASSWORD = your_16_char_google_app_password

How to get a Google App Password:
  1. Go to https://myaccount.google.com/apppasswords
  2. Enable 2-Step Verification first (if not already)
  3. Create an App Password → copy the 16-char code → paste as SMTP_PASSWORD
"""

import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def _send_email(
    smtp_email: str,
    smtp_password: str,
    to_email: str,
    subject: str,
    body_html: str,
) -> None:
    """Internal helper — runs in a background thread."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"MediGuide AI <{smtp_email}>"
        msg["To"]      = to_email

        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(smtp_email, smtp_password)
            server.sendmail(smtp_email, to_email, msg.as_string())

        print(f"[EMAIL SENT] Emergency alert -> {to_email}")

    except smtplib.SMTPAuthenticationError:
        print("[EMAIL ERROR] Gmail auth failed — check SMTP_EMAIL / SMTP_PASSWORD in .env")
        print("              Make sure you are using a Google App Password, not your normal password.")
    except smtplib.SMTPException as e:
        print(f"[EMAIL ERROR] SMTP error: {e}")
    except Exception as e:
        print(f"[EMAIL ERROR] Could not send email: {e}")


def send_emergency_alert(
    patient_name: str,
    patient_email: str,
    symptoms: str,
    risk_score: int,
    triage_level: str,
    to_email: str,
    smtp_email: str,
    smtp_password: str,
) -> None:
    """
    Sends a blood bank emergency alert email.
    Runs in a background thread — does NOT block the API response.
    Silently skips if SMTP credentials are not configured.
    """
    # Skip gracefully if not configured
    if not smtp_email or not smtp_password:
        print("[EMAIL SKIP] SMTP_EMAIL or SMTP_PASSWORD not set in .env — skipping email alert")
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    subject = f"🚨 EMERGENCY ALERT — MediGuide AI | Patient: {patient_name}"

    body_html = f"""
    <html><body style="font-family:Arial,sans-serif;background:#f5f5f5;padding:20px">
      <div style="max-width:580px;margin:auto;background:#fff;border-radius:10px;
                  border-top:5px solid #e53935;padding:30px">

        <h2 style="color:#e53935;margin-top:0">🚨 Emergency Blood Bank Alert</h2>
        <p style="color:#555">MediGuide AI has detected a high-risk emergency situation
           and is notifying the blood bank contact immediately.</p>

        <table style="width:100%;border-collapse:collapse;margin:20px 0">
          <tr style="background:#fff5f5">
            <td style="padding:10px;font-weight:bold;color:#333;border:1px solid #fcc">Patient Name</td>
            <td style="padding:10px;color:#555;border:1px solid #fcc">{patient_name}</td>
          </tr>
          <tr>
            <td style="padding:10px;font-weight:bold;color:#333;border:1px solid #fcc">Patient Email</td>
            <td style="padding:10px;color:#555;border:1px solid #fcc">{patient_email}</td>
          </tr>
          <tr style="background:#fff5f5">
            <td style="padding:10px;font-weight:bold;color:#333;border:1px solid #fcc">Symptoms Reported</td>
            <td style="padding:10px;color:#555;border:1px solid #fcc">{symptoms}</td>
          </tr>
          <tr>
            <td style="padding:10px;font-weight:bold;color:#333;border:1px solid #fcc">Risk Score</td>
            <td style="padding:10px;color:#e53935;font-weight:bold;border:1px solid #fcc">{risk_score}/100</td>
          </tr>
          <tr style="background:#fff5f5">
            <td style="padding:10px;font-weight:bold;color:#333;border:1px solid #fcc">Triage Level</td>
            <td style="padding:10px;color:#e53935;font-weight:bold;border:1px solid #fcc">{triage_level}</td>
          </tr>
          <tr>
            <td style="padding:10px;font-weight:bold;color:#333;border:1px solid #fcc">Alert Time</td>
            <td style="padding:10px;color:#555;border:1px solid #fcc">{now}</td>
          </tr>
        </table>

        <div style="background:#e53935;color:#fff;padding:15px;border-radius:8px;text-align:center">
          <strong>⚠️ Please prepare blood/emergency resources immediately.</strong><br>
          Call 108 if the patient has not already done so.
        </div>

        <p style="color:#aaa;font-size:12px;margin-top:20px;text-align:center">
          Sent automatically by MediGuide AI Emergency Detection System
        </p>
      </div>
    </body></html>
    """

    # Fire in a background thread so API response is instant
    thread = threading.Thread(
        target=_send_email,
        args=(smtp_email, smtp_password, to_email, subject, body_html),
        daemon=True,
    )
    thread.start()
