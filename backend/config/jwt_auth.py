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
    verifies it, and injects the verified admin_id as the route
    function's first argument (before any URL params like student_id).
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

        # Make the verified admin_id available to the route function
        request.admin_id = payload["admin_id"]
        request.admin_email = payload["email"]

        return f(*args, **kwargs)
    return wrapper
