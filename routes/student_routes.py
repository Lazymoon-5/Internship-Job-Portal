from flask import Blueprint, request, jsonify
from controllers.student_controller import (
    register_student,
    login_student,
    forgot_password,
    reset_password,
)

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
