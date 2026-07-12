"""
Admin controller — login and change password. No register_admin
function exists on purpose — admin accounts are created exclusively
via scripts/seed_admin.py, run manually by whoever manages the platform.
"""

from werkzeug.security import check_password_hash, generate_password_hash
from models.admin import find_by_email, find_by_id, update_password
from config.jwt_auth import generate_admin_token


def login_admin(data):
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return {
            "success": False,
            "message": "Email and password are required."
        }, 400

    admin = find_by_email(email)

    if not admin or not check_password_hash(admin.password_hash, password):
        return {
            "success": False,
            "message": "Invalid email or password."
        }, 401

    token = generate_admin_token(admin.id, admin.email)

    return {
        "success": True,
        "message": "Login successful.",
        "admin": admin.to_dict(),
        "token": token
    }, 200


def change_password(admin_id, data):
    current_password = data.get("current_password") or ""
    new_password = data.get("new_password") or ""
    confirm_password = data.get("confirm_password") or ""

    if not current_password or not new_password or not confirm_password:
        return {
            "success": False,
            "message": "Current password, new password, and confirm password are all required."
        }, 400

    admin = find_by_id(admin_id)
    if not admin:
        return {"success": False, "message": "Admin not found."}, 404

    if not check_password_hash(admin.password_hash, current_password):
        return {"success": False, "message": "Current password is incorrect."}, 401

    if new_password != confirm_password:
        return {"success": False, "message": "New passwords do not match."}, 400

    if len(new_password) < 10:
        return {
            "success": False,
            "message": "New password must be at least 10 characters long."
        }, 400

    new_hash = generate_password_hash(new_password)
    update_password(admin_id, new_hash)

    return {"success": True, "message": "Password updated successfully."}, 200
