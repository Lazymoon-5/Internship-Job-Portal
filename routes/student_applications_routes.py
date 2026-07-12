from flask import Blueprint, request, jsonify
from controllers.student_application_controller import (
    apply_to_job, get_my_applications, get_my_application_stats, get_my_application_detail
)
from config.jwt_auth import student_required

student_applications_bp = Blueprint("student_applications_routes", __name__, url_prefix="/api/student")


@student_applications_bp.route("/jobs/<int:job_id>/apply", methods=["POST"])
@student_required
def apply_route(job_id):
    data = request.get_json(silent=True) or {}
    response, status_code = apply_to_job(request.student_id, job_id, data)
    return jsonify(response), status_code


@student_applications_bp.route("/applications", methods=["GET"])
@student_required
def my_applications_route():
    response, status_code = get_my_applications(request.student_id, request.args)
    return jsonify(response), status_code


@student_applications_bp.route("/applications/stats", methods=["GET"])
@student_required
def my_application_stats_route():
    response, status_code = get_my_application_stats(request.student_id)
    return jsonify(response), status_code


@student_applications_bp.route("/applications/<int:application_id>", methods=["GET"])
@student_required
def my_application_detail_route(application_id):
    response, status_code = get_my_application_detail(request.student_id, application_id)
    return jsonify(response), status_code
