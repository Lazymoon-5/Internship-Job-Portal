"""
Email sending module — using Resend's HTTP API (not SMTP).

Why HTTP instead of SMTP: many free-tier hosts (including Render on
lower plans) block outbound SMTP ports (587/465) to prevent spam abuse.
Resend's API works over regular HTTPS, which is never blocked, so this
works reliably in production as well as locally.

Reads credentials from environment variables (.env):
    RESEND_API_KEY      — from Resend dashboard -> API Keys
    RESEND_SENDER_EMAIL  — a verified sender email/domain in your Resend account

SETUP:
1. Sign up free at resend.com
2. Dashboard -> API Keys -> Create API Key -> copy it (starts with "re_")
3. Dashboard -> Domains -> add + verify a sender (or use their provided
   test domain like "onboarding@resend.dev" while testing, which works
   immediately with no verification needed)
4. Put both values in .env (and in Render's Environment tab once deployed)
"""

import os
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
RESEND_SENDER_EMAIL = os.environ.get("RESEND_SENDER_EMAIL", "onboarding@resend.dev")
RESEND_API_URL = "https://api.resend.com/emails"


def send_email(to_email: str, subject: str, body_html: str) -> bool:
    """
    Sends an email via Resend's HTTP API. Returns True if sent
    successfully, False otherwise. Never raises — logs the error and
    returns False, so a failed email doesn't crash the whole request.
    """
    if not RESEND_API_KEY:
        print("[EMAIL] Skipped — RESEND_API_KEY not set in .env")
        return False

    payload = {
        "from": f"Placify <{RESEND_SENDER_EMAIL}>",
        "to": [to_email],
        "subject": subject,
        "html": body_html,
    }
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(RESEND_API_URL, json=payload, headers=headers, timeout=10)
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
