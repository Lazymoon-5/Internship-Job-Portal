"""
JWT auth utilities for Django API backend.
Protects routes so authenticated tokens are parsed and injected onto the request.
Enforces 15 minutes of inactivity session expiration across all user roles (Student, Client, Admin).
"""

import os
import jwt
import datetime
from functools import wraps
from django.http import JsonResponse

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

JWT_SECRET = os.environ.get("SECRET_KEY", "dev-secret-key-change-this")
JWT_ALGORITHM = "HS256"
# 15 minutes session expiry due to inactivity
TOKEN_EXPIRY_MINUTES = int(os.environ.get("JWT_EXPIRY_MINUTES", 15))


def generate_admin_token(admin_id: int, email: str) -> str:
    payload = {
        "admin_id": admin_id,
        "role": "admin",
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=TOKEN_EXPIRY_MINUTES),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def generate_student_token(student_id: int, email: str) -> str:
    payload = {
        "student_id": student_id,
        "role": "student",
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=TOKEN_EXPIRY_MINUTES),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def generate_client_token(client_id: int, email: str) -> str:
    payload = {
        "client_id": client_id,
        "role": "client",
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=TOKEN_EXPIRY_MINUTES),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str):
    """Returns (payload, error_message)."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Session expired due to 15 minutes of inactivity. Please log in again."
    except jwt.InvalidTokenError:
        return None, "Invalid authentication token."


verify_admin_token = verify_token


def _get_auth_header(req):
    if hasattr(req, "headers"):
        auth = req.headers.get("Authorization", "")
        if auth:
            return auth
    if hasattr(req, "META"):
        auth = req.META.get("HTTP_AUTHORIZATION", "")
        if auth:
            return auth
    return ""


def admin_required(f):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        auth_header = _get_auth_header(request)

        if not auth_header.startswith("Bearer "):
            return JsonResponse({
                "success": False,
                "message": "Missing or malformed Authorization header. Expected: Bearer <token>"
            }, status=401)

        token = auth_header.split("Bearer ", 1)[1].strip()
        payload, error = verify_token(token)

        if error:
            return JsonResponse({"success": False, "message": error}, status=401)

        if payload.get("role") != "admin":
            return JsonResponse({"success": False, "message": "This token is not valid for admin routes."}, status=401)

        request.admin_id = payload["admin_id"]
        request.admin_email = payload["email"]

        return f(request, *args, **kwargs)
    return wrapper


def student_required(f):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        auth_header = _get_auth_header(request)

        if not auth_header.startswith("Bearer "):
            return JsonResponse({
                "success": False,
                "message": "Missing or malformed Authorization header. Expected: Bearer <token>"
            }, status=401)

        token = auth_header.split("Bearer ", 1)[1].strip()
        payload, error = verify_token(token)

        if error:
            return JsonResponse({"success": False, "message": error}, status=401)

        if payload.get("role") != "student":
            return JsonResponse({"success": False, "message": "This token is not valid for student routes."}, status=401)

        request.student_id = payload["student_id"]
        request.student_email = payload["email"]

        return f(request, *args, **kwargs)
    return wrapper


def client_required(f):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        auth_header = _get_auth_header(request)

        if not auth_header.startswith("Bearer "):
            return JsonResponse({
                "success": False,
                "message": "Missing or malformed Authorization header. Expected: Bearer <token>"
            }, status=401)

        token = auth_header.split("Bearer ", 1)[1].strip()
        payload, error = verify_token(token)

        if error:
            return JsonResponse({"success": False, "message": error}, status=401)

        if payload.get("role") != "client":
            return JsonResponse({"success": False, "message": "This token is not valid for client routes."}, status=401)

        request.client_id = payload["client_id"]
        request.client_email = payload["email"]

        return f(request, *args, **kwargs)
    return wrapper
