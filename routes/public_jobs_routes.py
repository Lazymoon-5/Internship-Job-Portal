from flask import Blueprint, request, jsonify
from controllers.public_job_controller import browse_public_jobs, get_public_job_detail

public_jobs_bp = Blueprint("public_jobs_routes", __name__, url_prefix="/api/jobs")


@public_jobs_bp.route("", methods=["GET"])
def browse_public_jobs_route():
    """
    GET /api/jobs?limit=5  -> for Home page "Latest Jobs" preview
    GET /api/jobs?search=...&job_type=...&location=...&page=1&per_page=10
        -> for a full public job listing page, if one exists
    No authentication required.
    """
    response, status_code = browse_public_jobs(request.args)
    return jsonify(response), status_code


@public_jobs_bp.route("/<int:job_id>", methods=["GET"])
def public_job_detail_route(job_id):
    response, status_code = get_public_job_detail(job_id)
    return jsonify(response), status_code
