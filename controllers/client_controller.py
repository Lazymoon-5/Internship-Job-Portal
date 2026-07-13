"""
Client (Company) controller — business logic for register/login/
forgot-password/reset-password/OTP verification.

Mirrors controllers/student_controller.py exactly, but for Clients.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from models.client import (
    add_client,
    find_by_email,
    find_by_id,
    update_password,
    mark_verified,
    create_reset_token,
    get_email_for_token,
    invalidate_token,
    create_otp,
    verify_otp,
)
from config.email_service import send_otp_email, send_reset_password_email


def register_client(data):
    """
    Expects data = {company_name, email, password, industry, website (optional)}

    Creates the client as UNVERIFIED and sends an OTP to their email.
    They must call verify_registration_otp before they can log in.
    """
    required_fields = ["company_name", "email", "password", "industry"]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return {
            "success": False,
            "message": f"Missing required field(s): {', '.join(missing)}"
        }, 400

    email = data["email"].strip().lower()

    if find_by_email(email):
        return {
            "success": False,
            "message": "An account with this email already exists."
        }, 409

    password_hash = generate_password_hash(data["password"])

    client = add_client({
        "company_name": data["company_name"].strip(),
        "email": email,
        "password_hash": password_hash,
        "industry": data["industry"].strip(),
        "website": (data.get("website") or "").strip(),
    })

    otp_code = create_otp(email, purpose="registration")
    email_sent = send_otp_email(email, otp_code)

    response = {
        "success": True,
        "message": "Registered successfully. An OTP has been sent to your email — verify it to activate your account.",
        "client": client.to_dict(),
        "email_sent": email_sent,
    }
    if not email_sent:
        response["dev_otp"] = otp_code

    return response, 201


def verify_registration_otp(data):
    """
    Expects data = {email, otp}
    """
    email = (data.get("email") or "").strip().lower()
    otp_code = (data.get("otp") or "").strip()

    if not email or not otp_code:
        return {
            "success": False,
            "message": "Email and OTP are required."
        }, 400

    success, message = verify_otp(email, otp_code, purpose="registration")

    if not success:
        return {"success": False, "message": message}, 400

    mark_verified(email)

    return {
        "success": True,
        "message": "Email verified successfully. You can now log in."
    }, 200


def resend_otp(data):
    """
    Expects data = {email, purpose} — purpose defaults to 'registration'
    """
    email = (data.get("email") or "").strip().lower()
    purpose = (data.get("purpose") or "registration").strip()

    if not email:
        return {"success": False, "message": "Email is required."}, 400

    client = find_by_email(email)
    if not client:
        return {"success": False, "message": "No account found with this email."}, 404

    if purpose == "registration" and client.is_verified:
        return {"success": False, "message": "This account is already verified."}, 400

    otp_code = create_otp(email, purpose=purpose)
    email_sent = send_otp_email(email, otp_code)

    response = {
        "success": True,
        "message": "A new OTP has been sent to your email.",
        "email_sent": email_sent,
    }
    if not email_sent:
        response["dev_otp"] = otp_code

    return response, 200


def login_client(data):
    """
    Expects data = {email, password}
    Blocks login if the account hasn't verified its OTP yet.
    """
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return {
            "success": False,
            "message": "Email and password are required."
        }, 400

    client = find_by_email(email)

    if not client or not check_password_hash(client.password_hash, password):
        return {
            "success": False,
            "message": "Invalid email or password."
        }, 401

    if not client.is_verified:
        return {
            "success": False,
            "message": "Please verify your email with the OTP sent to you before logging in.",
            "requires_verification": True
        }, 403

    if client.admin_status == "Blocked":
        return {
            "success": False,
            "message": "Your company account has been blocked by an administrator. Contact support for help."
        }, 403

    from config.jwt_auth import generate_client_token
    token = generate_client_token(client.id, client.email)

    return {
        "success": True,
        "message": "Login successful.",
        "client": client.to_dict(),
        "token": token
    }, 200


def forgot_password(data):
    """
    Expects data = { "email": str }
    Sends a real email via config/email_service.py. Falls back to
    returning dev_reset_link in the response if email delivery fails,
    so testing isn't blocked.
    """
    email = (data.get("email") or "").strip().lower()

    if not email:
        return {"success": False, "message": "Email is required."}, 400

    client = find_by_email(email)

    # Same generic message whether or not the email exists — prevents
    # account enumeration.
    if not client:
        return {
            "success": True,
            "message": "If an account with this email exists, a password reset link has been sent."
        }, 200

    token = create_reset_token(email)
    reset_link = f"http://localhost:3000/reset-password?token={token}"

    email_sent = send_reset_password_email(email, reset_link)

    response = {
        "success": True,
        "message": "If an account with this email exists, a password reset link has been sent.",
    }
    if not email_sent:
        response["dev_reset_link"] = reset_link

    return response, 200


def reset_password(data):
    token = data.get("token") or ""
    new_password = data.get("new_password") or ""
    confirm_password = data.get("confirm_password") or ""

    if not token:
        return {"success": False, "message": "Reset token is required."}, 400

    if not new_password or not confirm_password:
        return {
            "success": False,
            "message": "New password and confirm password are required."
        }, 400

    if new_password != confirm_password:
        return {"success": False, "message": "Passwords do not match."}, 400

    if len(new_password) < 6:
        return {
            "success": False,
            "message": "Password must be at least 6 characters long."
        }, 400

    email = get_email_for_token(token)

    if not email:
        return {
            "success": False,
            "message": "This reset link is invalid or has expired. Please request a new one."
        }, 400

    new_password_hash = generate_password_hash(new_password)
    update_password(email, new_password_hash)
    invalidate_token(token)

    return {
        "success": True,
        "message": "Password has been reset successfully. You can now log in with your new password."
    }, 200


def change_password(client_id, data):
    """Requires the client to be logged in (client_id from verified JWT)."""
    current_password = data.get("current_password") or ""
    new_password = data.get("new_password") or ""
    confirm_password = data.get("confirm_password") or ""

    if not current_password or not new_password or not confirm_password:
        return {
            "success": False,
            "message": "Current password, new password, and confirm password are all required."
        }, 400

    client = find_by_id(client_id)
    if not client:
        return {"success": False, "message": "Company account not found."}, 404

    if not check_password_hash(client.password_hash, current_password):
        return {"success": False, "message": "Current password is incorrect."}, 401

    if new_password != confirm_password:
        return {"success": False, "message": "New passwords do not match."}, 400

    if len(new_password) < 8:
        return {
            "success": False,
            "message": "New password must be at least 8 characters long."
        }, 400

    new_hash = generate_password_hash(new_password)
    update_password(client.email, new_hash)

    return {"success": True, "message": "Password updated successfully."}, 200
