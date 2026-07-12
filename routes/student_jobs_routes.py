from flask import Blueprint, request, jsonify
from controllers.student_job_controller import browse_jobs, get_job_detail
from config.jwt_auth import student_required

student_jobs_bp = Blueprint("student_jobs_routes", __name__, url_prefix="/api/student/jobs")


@student_jobs_bp.route("", methods=["GET"])
@student_required
def browse_jobs_route():
    response, status_code = browse_jobs(request.args)
    return jsonify(response), status_code


@student_jobs_bp.route("/<int:job_id>", methods=["GET"])
@student_required
def job_detail_route(job_id):
    response, status_code = get_job_detail(job_id)
    return jsonify(response), status_code
