from flask import Blueprint, request, jsonify
from controllers.client_controller import (
    register_client,
    login_client,
    forgot_password,
    reset_password,
    verify_registration_otp,
    resend_otp,
)

client_bp = Blueprint("client_routes", __name__, url_prefix="/api/client")


@client_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    response, status_code = register_client(data)
    return jsonify(response), status_code


@client_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    response, status_code = login_client(data)
    return jsonify(response), status_code


@client_bp.route("/verify-otp", methods=["POST"])
def verify_otp_route():
    data = request.get_json(silent=True) or {}
    response, status_code = verify_registration_otp(data)
    return jsonify(response), status_code


@client_bp.route("/resend-otp", methods=["POST"])
def resend_otp_route():
    data = request.get_json(silent=True) or {}
    response, status_code = resend_otp(data)
    return jsonify(response), status_code


@client_bp.route("/forgot-password", methods=["POST"])
def forgot_password_route():
    data = request.get_json(silent=True) or {}
    response, status_code = forgot_password(data)
    return jsonify(response), status_code


@client_bp.route("/reset-password", methods=["POST"])
def reset_password_route():
    data = request.get_json(silent=True) or {}
    response, status_code = reset_password(data)
    return jsonify(response), status_code
