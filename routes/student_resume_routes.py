from flask import Blueprint, request, jsonify
from controllers.student_resume_controller import (
    get_resumes, add_resume, set_primary_resume, delete_resume
)
from config.jwt_auth import student_required

student_resume_bp = Blueprint("student_resume_routes", __name__, url_prefix="/api/student/resumes")


@student_resume_bp.route("", methods=["GET"])
@student_required
def list_resumes_route():
    response, status_code = get_resumes(request.student_id)
    return jsonify(response), status_code


@student_resume_bp.route("", methods=["POST"])
@student_required
def add_resume_route():
    data = request.get_json(silent=True) or {}
    response, status_code = add_resume(request.student_id, data)
    return jsonify(response), status_code


@student_resume_bp.route("/<int:resume_id>/set-primary", methods=["PATCH"])
@student_required
def set_primary_route(resume_id):
    response, status_code = set_primary_resume(request.student_id, resume_id)
    return jsonify(response), status_code


@student_resume_bp.route("/<int:resume_id>", methods=["DELETE"])
@student_required
def delete_resume_route(resume_id):
    response, status_code = delete_resume(request.student_id, resume_id)
    return jsonify(response), status_code
