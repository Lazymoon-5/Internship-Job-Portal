"""
Email sending module — real SMTP via Gmail.

Uses Python's built-in smtplib, no extra dependency needed.
Reads credentials from environment variables (.env):
    EMAIL_ADDRESS   — the dummy Gmail address
    EMAIL_APP_PASSWORD — the 16-character Gmail App Password
                         (NOT the normal Gmail login password —
                         Gmail blocks regular passwords for SMTP)

HOW TO GET AN APP PASSWORD:
1. Turn on 2-Step Verification on the Gmail account.
2. Go to https://myaccount.google.com/apppasswords
3. Generate one for "Mail" — copy the 16-character code.
4. Put it in .env as EMAIL_APP_PASSWORD (no spaces).
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD")


def send_email(to_email: str, subject: str, body_html: str) -> bool:
    """
    Sends an email. Returns True if sent successfully, False otherwise.
    Never raises — logs the error and returns False, so a failed email
    doesn't crash the whole request (e.g. OTP generation should still
    succeed and be returned/logged even if the email bounces).
    """
    if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
        print("[EMAIL] Skipped — EMAIL_ADDRESS or EMAIL_APP_PASSWORD not set in .env")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        print(f"[EMAIL] Sent to {to_email}: {subject}")
        return True
    except Exception as e:
        print(f"[EMAIL] Failed to send to {to_email}: {e}")
        return False


def send_otp_email(to_email: str, otp_code: str) -> bool:
    subject = "Your CampusBridge Verification Code"
    body_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto;">
        <h2 style="color: #1D3E82;">CampusBridge</h2>
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
    subject = "Reset Your CampusBridge Password"
    body_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto;">
        <h2 style="color: #1D3E82;">CampusBridge</h2>
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
