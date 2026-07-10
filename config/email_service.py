"""
Email sending module — using Brevo's HTTP API (not SMTP).

Why HTTP instead of SMTP: many free-tier hosts (including Render on
lower plans) block outbound SMTP ports (587/465) to prevent spam abuse.
Brevo's API works over regular HTTPS, which is never blocked, so this
works reliably in production as well as locally.

Reads credentials from environment variables (.env):
    BREVO_API_KEY      — from Brevo dashboard -> Settings -> SMTP & API -> API Keys
    BREVO_SENDER_EMAIL  — a verified sender email in your Brevo account

SETUP:
1. Sign up free at brevo.com
2. Settings -> SMTP & API -> API Keys -> Generate a new API key
3. Senders, Domains & Dedicated IPs -> Senders -> add + verify your email
4. Put both values in .env (and in Render's Environment tab once deployed)
"""

import os
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BREVO_API_KEY = os.environ.get("BREVO_API_KEY")
BREVO_SENDER_EMAIL = os.environ.get("BREVO_SENDER_EMAIL")
BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def send_email(to_email: str, subject: str, body_html: str) -> bool:
    """
    Sends an email via Brevo's HTTP API. Returns True if sent
    successfully, False otherwise. Never raises — logs the error and
    returns False, so a failed email doesn't crash the whole request.
    """
    if not BREVO_API_KEY or not BREVO_SENDER_EMAIL:
        print("[EMAIL] Skipped — BREVO_API_KEY or BREVO_SENDER_EMAIL not set in .env")
        return False

    payload = {
        "sender": {"email": BREVO_SENDER_EMAIL, "name": "Placify"},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": body_html,
    }
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }

    try:
        response = requests.post(BREVO_API_URL, json=payload, headers=headers, timeout=10)
        if response.status_code in (200, 201):
            print(f"[EMAIL] Sent to {to_email}: {subject}")
            return True
        else:
            print(f"[EMAIL] Failed to send to {to_email}: {response.status_code} {response.text}")
            return False
    except Exception as e:
        print(f"[EMAIL] Failed to send to {to_email}: {e}")
        return False


def send_otp_email(to_email: str, otp_code: str) -> bool:
    subject = "Your Placify Verification Code"
    body_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto;">
        <h2 style="color: #1D3E82;">Placify</h2>
        <p>Your verification code is:</p>
        <div style="font-size: 28px; font-weight: bold; letter-spacing: 4px;
                    background: #F5F6F8; padding: 16px; text-align: center;
                    border-radius: 8px; color: #14213D;">
            {otp_code}
        </div>
        <p style="color: #6B7280; font-size: 13px; margin-top: 16px;">
            This code expires in 10 minutes. If you didn't request this, ignore this email.
        </p>
    </div>
    """
    return send_email(to_email, subject, body_html)


def send_reset_password_email(to_email: str, reset_link: str) -> bool:
    subject = "Reset Your Placify Password"
    body_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto;">
        <h2 style="color: #1D3E82;">Placify</h2>
        <p>We received a request to reset your password. Click below to continue:</p>
        <a href="{reset_link}"
           style="display: inline-block; background: #D98E04; color: white;
                  padding: 12px 24px; border-radius: 8px; text-decoration: none;
                  font-weight: bold; margin: 12px 0;">
            Reset Password
        </a>
        <p style="color: #6B7280; font-size: 13px;">
            This link expires in 30 minutes. If you didn't request this, ignore this email.
        </p>
    </div>
    """
    return send_email(to_email, subject, body_html)