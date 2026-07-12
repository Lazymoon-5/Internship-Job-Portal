"""
Student controller — business logic for register/login/forgot-password/
reset-password/OTP verification/Google login.

Kept separate from routes so routes stay thin (just receive request,
call controller, return response).
"""

from werkzeug.security import generate_password_hash, check_password_hash
from models.student import (
    add_student,
    find_by_email,
    update_password,
    mark_verified,
    find_or_create_by_google,
    create_reset_token,
    get_email_for_token,
    invalidate_token,
    create_otp,
    verify_otp,
)
from config.email_service import send_otp_email, send_reset_password_email


def register_student(data):
    """
    Expects data = {name, email, password, college, branch}

    Creates the student as UNVERIFIED and sends an OTP to their email.
    They must call verify_otp (purpose='registration') before they can
    log in — see login_student() below, which blocks unverified accounts.
    """
    required_fields = ["name", "email", "password", "college", "branch"]
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

    student = add_student({
        "name": data["name"].strip(),
        "email": email,
        "password_hash": password_hash,
        "college": data["college"].strip(),
        "branch": data["branch"].strip(),
    })

    otp_code = create_otp(email, purpose="registration")
    email_sent = send_otp_email(email, otp_code)

    response = {
        "success": True,
        "message": "Registered successfully. An OTP has been sent to your email — verify it to activate your account.",
        "student": student.to_dict(),
        "email_sent": email_sent,
    }
    # Dev convenience only — remove once email delivery is confirmed
    # reliable in your environment. Lets you test without checking inbox.
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

    student = find_by_email(email)
    if not student:
        return {"success": False, "message": "No account found with this email."}, 404

    if purpose == "registration" and student.is_verified:
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


def login_student(data):
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

    student = find_by_email(email)

    if not student or not check_password_hash(student.password_hash, password):
        return {
            "success": False,
            "message": "Invalid email or password."
        }, 401

    if not student.is_verified:
        return {
            "success": False,
            "message": "Please verify your email with the OTP sent to you before logging in.",
            "requires_verification": True
        }, 403

    if student.status == "Blocked":
        return {
            "success": False,
            "message": "Your account has been blocked by an administrator. Contact support for help."
        }, 403

    from config.jwt_auth import generate_student_token
    token = generate_student_token(student.id, student.email)

    return {
        "success": True,
        "message": "Login successful.",
        "student": student.to_dict(),
        "token": token
    }, 200


def google_login(data):
    """
    Expects data = { "id_token": str } — the ID token returned by
    Google Sign-In on the frontend after the user picks their Google account.

    REQUIRES: GOOGLE_CLIENT_ID set in .env (from Google Cloud Console —
    see config/google_auth.py for setup instructions). Until that's
    configured, this returns a clear 501 error instead of crashing.
    """
    id_token_str = data.get("id_token")

    if not id_token_str:
        return {"success": False, "message": "id_token is required."}, 400

    from config.google_auth import verify_google_token, GOOGLE_CLIENT_ID

    if not GOOGLE_CLIENT_ID:
        return {
            "success": False,
            "message": "Google Sign-In is not configured yet on the server (missing GOOGLE_CLIENT_ID)."
        }, 501

    payload, error = verify_google_token(id_token_str)
    if error:
        return {"success": False, "message": error}, 401

    student = find_or_create_by_google(
        google_id=payload["sub"],
        email=payload["email"],
        name=payload.get("name", payload["email"].split("@")[0]),
    )

    from config.jwt_auth import generate_student_token
    token = generate_student_token(student.id, student.email)

    return {
        "success": True,
        "message": "Login successful via Google.",
        "student": student.to_dict(),
        "token": token
    }, 200


def forgot_password(data):
    """
    Expects data = { "email": str }
    Sends a REAL email now (via config/email_service.py) instead of
    only returning the link — dev_reset_link stays as a fallback in
    case email delivery fails, so testing isn't blocked.
    """
    email = (data.get("email") or "").strip().lower()

    if not email:
        return {"success": False, "message": "Email is required."}, 400

    student = find_by_email(email)

    if not student:
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
