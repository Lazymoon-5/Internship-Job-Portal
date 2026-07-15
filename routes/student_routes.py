from flask import Blueprint, request, jsonify
from controllers.student_controller import (
    register_student,
    login_student,
    forgot_password,
    reset_password,
    verify_registration_otp,
    resend_otp,
    google_login,
    change_password,
)
from config.jwt_auth import student_required

student_bp = Blueprint("student_routes", __name__, url_prefix="/api/student")


@student_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    response, status_code = register_student(data)
    return jsonify(response), status_code


@student_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    response, status_code = login_student(data)
    return jsonify(response), status_code


@student_bp.route("/verify-otp", methods=["POST"])
def verify_otp_route():
    data = request.get_json(silent=True) or {}
    response, status_code = verify_registration_otp(data)
    return jsonify(response), status_code


@student_bp.route("/resend-otp", methods=["POST"])
def resend_otp_route():
    data = request.get_json(silent=True) or {}
    response, status_code = resend_otp(data)
    return jsonify(response), status_code


@student_bp.route("/google-login", methods=["POST"])
def google_login_route():
    data = request.get_json(silent=True) or {}
    response, status_code = google_login(data)
    return jsonify(response), status_code


@student_bp.route("/forgot-password", methods=["POST"])
def forgot_password_route():
    data = request.get_json(silent=True) or {}
    response, status_code = forgot_password(data)
    return jsonify(response), status_code


@student_bp.route("/reset-password", methods=["POST"])
def reset_password_route():
    data = request.get_json(silent=True) or {}
    response, status_code = reset_password(data)
    return jsonify(response), status_code


@student_bp.route("/change-password", methods=["POST"])
@student_required
def change_password_route():
    data = request.get_json(silent=True) or {}
    response, status_code = change_password(request.student_id, data)
    return jsonify(response), status_code
