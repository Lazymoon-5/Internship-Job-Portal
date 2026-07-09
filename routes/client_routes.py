from flask import Blueprint, request, jsonify
from controllers.client_controller import (
    register_client,
    login_client,
    forgot_password,
    reset_password,
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
