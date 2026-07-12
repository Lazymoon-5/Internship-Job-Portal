from flask import Blueprint, request, jsonify
from controllers.student_profile_controller import (
    get_profile, update_profile, update_profile_photo,
    add_certification, delete_certification, add_skill, delete_skill
)
from config.jwt_auth import student_required

student_profile_bp = Blueprint("student_profile_routes", __name__, url_prefix="/api/student/profile")


@student_profile_bp.route("", methods=["GET"])
@student_required
def get_profile_route():
    response, status_code = get_profile(request.student_id)
    return jsonify(response), status_code


@student_profile_bp.route("", methods=["PUT"])
@student_required
def update_profile_route():
    data = request.get_json(silent=True) or {}
    mark_completed = data.pop("mark_completed", False)
    response, status_code = update_profile(request.student_id, data, mark_completed)
    return jsonify(response), status_code


@student_profile_bp.route("/photo", methods=["POST"])
@student_required
def update_photo_route():
    data = request.get_json(silent=True) or {}
    response, status_code = update_profile_photo(request.student_id, data)
    return jsonify(response), status_code


@student_profile_bp.route("/certifications", methods=["POST"])
@student_required
def add_certification_route():
    data = request.get_json(silent=True) or {}
    response, status_code = add_certification(request.student_id, data)
    return jsonify(response), status_code


@student_profile_bp.route("/certifications/<int:certification_id>", methods=["DELETE"])
@student_required
def delete_certification_route(certification_id):
    response, status_code = delete_certification(request.student_id, certification_id)
    return jsonify(response), status_code


@student_profile_bp.route("/skills", methods=["POST"])
@student_required
def add_skill_route():
    data = request.get_json(silent=True) or {}
    response, status_code = add_skill(request.student_id, data)
    return jsonify(response), status_code


@student_profile_bp.route("/skills/<int:skill_id>", methods=["DELETE"])
@student_required
def delete_skill_route(skill_id):
    response, status_code = delete_skill(request.student_id, skill_id)
    return jsonify(response), status_code
