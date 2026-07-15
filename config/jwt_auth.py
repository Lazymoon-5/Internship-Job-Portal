"""
JWT auth utilities — used to protect all Admin routes so only someone
who actually logged in successfully (with valid admin credentials) can
call management endpoints like block/approve/delete.

HOW THIS WORKS:
1. POST /api/admin/login succeeds -> server generates a signed token
   containing the admin's id, and sends it back in the response.
2. The frontend stores this token (e.g. in memory or localStorage) and
   sends it on every subsequent Admin API request as a header:
       Authorization: Bearer <token>
3. Every protected route is wrapped with @admin_required, which reads
   that header, verifies the token's signature and expiry, and only
   then allows the request through. If the token is missing, invalid,
   or expired, the request is rejected with 401 before any business
   logic runs.

Tokens expire after 24 hours — after that, the admin must log in again.
"""

import os
import jwt
import datetime
from functools import wraps
from flask import request, jsonify

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

JWT_SECRET = os.environ.get("SECRET_KEY", "dev-secret-key-change-this")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 24


def generate_admin_token(admin_id: int, email: str) -> str:
    payload = {
        "admin_id": admin_id,
        "role": "admin",
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRY_HOURS),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def generate_student_token(student_id: int, email: str) -> str:
    payload = {
        "student_id": student_id,
        "role": "student",
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRY_HOURS),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def generate_client_token(client_id: int, email: str) -> str:
    payload = {
        "client_id": client_id,
        "role": "client",
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRY_HOURS),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_admin_token(token: str):
    """Returns (payload, error_message). payload contains admin_id, email."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Session expired. Please log in again."
    except jwt.InvalidTokenError:
        return None, "Invalid authentication token."


def admin_required(f):
    """
    Decorator — put this on any route that should only be callable by
    a logged-in admin. Reads the Authorization: Bearer <token> header,
    verifies it, and injects the verified admin_id as request.admin_id.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({
                "success": False,
                "message": "Missing or malformed Authorization header. Expected: Bearer <token>"
            }), 401

        token = auth_header.split("Bearer ", 1)[1].strip()
        payload, error = verify_admin_token(token)

        if error:
            return jsonify({"success": False, "message": error}), 401

        if payload.get("role") != "admin":
            return jsonify({"success": False, "message": "This token is not valid for admin routes."}), 401

        request.admin_id = payload["admin_id"]
        request.admin_email = payload["email"]

        return f(*args, **kwargs)
    return wrapper


def student_required(f):
    """
    Same pattern as admin_required, but for Student routes. Injects the
    verified student_id as request.student_id — so a student can only
    ever access/edit THEIR OWN data, never another student's, since the
    id comes from the signed token, not from anything the client can
    tamper with.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({
                "success": False,
                "message": "Missing or malformed Authorization header. Expected: Bearer <token>"
            }), 401

        token = auth_header.split("Bearer ", 1)[1].strip()
        payload, error = verify_admin_token(token)

        if error:
            return jsonify({"success": False, "message": error}), 401

        if payload.get("role") != "student":
            return jsonify({"success": False, "message": "This token is not valid for student routes."}), 401

        request.student_id = payload["student_id"]
        request.student_email = payload["email"]

        return f(*args, **kwargs)
    return wrapper


def client_required(f):
    """
    Same pattern, for Client (Company) routes. Injects the verified
    client_id as request.client_id — a company can only ever access/edit
    THEIR OWN jobs and applicants, never another company's.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({
                "success": False,
                "message": "Missing or malformed Authorization header. Expected: Bearer <token>"
            }), 401

        token = auth_header.split("Bearer ", 1)[1].strip()
        payload, error = verify_admin_token(token)

        if error:
            return jsonify({"success": False, "message": error}), 401

        if payload.get("role") != "client":
            return jsonify({"success": False, "message": "This token is not valid for client routes."}), 401

        request.client_id = payload["client_id"]
        request.client_email = payload["email"]

        return f(*args, **kwargs)
    return wrapper
