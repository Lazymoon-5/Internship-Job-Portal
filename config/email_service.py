"""
Email sending module — using SendGrid's HTTP API (not SMTP).

Why HTTP instead of SMTP: many free-tier hosts (including Render on
lower plans) block outbound SMTP ports (587/465) to prevent spam abuse.
SendGrid's API works over regular HTTPS, which is never blocked, so
this works reliably in production as well as locally.

Reads credentials from environment variables (.env):
    SENDGRID_API_KEY      — from SendGrid dashboard -> Settings -> API Keys
    SENDGRID_SENDER_EMAIL  — a verified sender email in your SendGrid account

SETUP:
1. Sign up free at sendgrid.com (free tier: 100 emails/day forever)
2. Settings -> API Keys -> Create API Key -> Full Access (or "Restricted
   Access" with at least "Mail Send" permission) -> copy it (starts with "SG.")
3. Settings -> Sender Authentication -> verify a Single Sender (fastest —
   just verifies one email address, no domain needed) OR authenticate a
   whole domain for better deliverability
4. Put both values in .env (and in Render's Environment tab once deployed)
"""

import os
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
SENDGRID_SENDER_EMAIL = os.environ.get("SENDGRID_SENDER_EMAIL")
SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"


def send_email(to_email: str, subject: str, body_html: str) -> bool:
    """
    Sends an email via SendGrid's HTTP API. Returns True if sent
    successfully, False otherwise. Never raises — logs the error and
    returns False, so a failed email doesn't crash the whole request.
    """
    if not SENDGRID_API_KEY or not SENDGRID_SENDER_EMAIL:
        print("[EMAIL] Skipped — SENDGRID_API_KEY or SENDGRID_SENDER_EMAIL not set in .env")
        return False

    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": SENDGRID_SENDER_EMAIL, "name": "Placify"},
        "subject": subject,
        "content": [{"type": "text/html", "value": body_html}],
    }
    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(SENDGRID_API_URL, json=payload, headers=headers, timeout=10)
        # SendGrid returns 202 Accepted on success — no response body
        if response.status_code == 202:
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


def send_recruiter_message_email(to_email: str, company_name: str, subject: str, message: str) -> bool:
    """Used by 'Message All Applicants' — a free-text message from a
    company to a candidate about a specific job application."""
    full_subject = f"{company_name}: {subject}"
    body_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto;">
        <h2 style="color: #1D3E82;">Placify</h2>
        <p style="color: #6B7280; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;">
            Message from {company_name}
        </p>
        <div style="background: #F5F6F8; padding: 16px; border-radius: 8px; white-space: pre-wrap;">
            {message}
        </div>
        <p style="color: #6B7280; font-size: 13px; margin-top: 16px;">
            This message was sent via Placify regarding your job application.
        </p>
    </div>
    """
    return send_email(to_email, full_subject, body_html)


def send_contact_form_notification(submitter_name: str, submitter_email: str, message: str) -> bool:
    """
    Sends the Contact page submission to the TEAM's own inbox (not the
    person who submitted it) — reads CONTACT_NOTIFICATION_EMAIL from
    .env, falling back to SENDGRID_SENDER_EMAIL if not set separately.
    """
    import os
    notification_email = os.environ.get("CONTACT_NOTIFICATION_EMAIL") or SENDGRID_SENDER_EMAIL

    if not notification_email:
        print("[EMAIL] Skipped contact notification — no CONTACT_NOTIFICATION_EMAIL or SENDGRID_SENDER_EMAIL set")
        return False

    subject = f"New Contact Form Submission from {submitter_name}"
    body_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto;">
        <h2 style="color: #1D3E82;">Placify — New Contact Submission</h2>
        <p><strong>Name:</strong> {submitter_name}</p>
        <p><strong>Email:</strong> {submitter_email}</p>
        <p><strong>Message:</strong></p>
        <div style="background: #F5F6F8; padding: 16px; border-radius: 8px; white-space: pre-wrap;">
            {message}
        </div>
        <p style="color: #6B7280; font-size: 13px; margin-top: 16px;">
            Reply directly to {submitter_email} to respond to this inquiry.
        </p>
    </div>
    """
    return send_email(notification_email, subject, body_html)
