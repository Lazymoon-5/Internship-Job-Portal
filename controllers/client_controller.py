"""
Client (Company) controller — business logic for register/login/
forgot-password/reset-password.

Kept separate from routes so that when MySQL is added later,
only the model layer changes, not this logic.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from models.client import (
    Client,
    add_client,
    find_by_email,
    update_password,
    create_reset_token,
    get_email_for_token,
    invalidate_token,
)


def register_client(data):
    """
    Expects data = {
        "company_name": str,
        "email": str,
        "password": str,
        "industry": str,
        "website": str (optional)
    }
    Returns (response_dict, status_code)
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

    client = Client(
        company_name=data["company_name"].strip(),
        email=email,
        password_hash=password_hash,
        industry=data["industry"].strip(),
        website=(data.get("website") or "").strip(),
    )
    add_client(client)

    return {
        "success": True,
        "message": "Company registered successfully.",
        "client": client.to_dict()
    }, 201


def login_client(data):
    """
    Expects data = {
        "email": str,
        "password": str
    }
    Returns (response_dict, status_code)
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

    return {
        "success": True,
        "message": "Login successful.",
        "client": client.to_dict()
    }, 200


def forgot_password(data):
    """
    Expects data = { "email": str }

    NOTE: No real email service is wired up yet. For now this returns
    the reset link directly in the response (and prints it to the
    console) so the flow can be tested end-to-end. Once an email
    provider is added, replace the print(...) line with an actual send.
    """
    email = (data.get("email") or "").strip().lower()

    if not email:
        return {
            "success": False,
            "message": "Email is required."
        }, 400

    client = find_by_email(email)

    # Same generic message whether or not the email exists, to avoid
    # letting people probe which emails are registered.
    if not client:
        return {
            "success": True,
            "message": "If an account with this email exists, a password reset link has been sent."
        }, 200

    token = create_reset_token(email)
    reset_link = f"http://localhost:3000/reset-password?token={token}"

    print(f"[MOCK EMAIL] Password reset link for {email}: {reset_link}")

    return {
        "success": True,
        "message": "If an account with this email exists, a password reset link has been sent.",
        "dev_reset_link": reset_link
    }, 200


def reset_password(data):
    """
    Expects data = {
        "token": str,
        "new_password": str,
        "confirm_password": str
    }
    """
    token = data.get("token") or ""
    new_password = data.get("new_password") or ""
    confirm_password = data.get("confirm_password") or ""

    if not token:
        return {
            "success": False,
            "message": "Reset token is required."
        }, 400

    if not new_password or not confirm_password:
        return {
            "success": False,
            "message": "New password and confirm password are required."
        }, 400

    if new_password != confirm_password:
        return {
            "success": False,
            "message": "Passwords do not match."
        }, 400

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
