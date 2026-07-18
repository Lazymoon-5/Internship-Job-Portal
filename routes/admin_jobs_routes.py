from flask import Blueprint, request, jsonify
from controllers.admin_job_controller import (
    get_jobs, get_job_moderation_stats, get_job_detail, approve_job, reject_job, close_job
)
from config.jwt_auth import admin_required

admin_jobs_bp = Blueprint("admin_jobs_routes", __name__, url_prefix="/api/admin/jobs")


@admin_jobs_bp.route("", methods=["GET"])
@admin_required
def list_jobs_route():
    response, status_code = get_jobs(request.args)
    return jsonify(response), status_code


@admin_jobs_bp.route("/stats", methods=["GET"])
@admin_required
def job_stats_route():
    response, status_code = get_job_moderation_stats()
    return jsonify(response), status_code


@admin_jobs_bp.route("/<int:job_id>", methods=["GET"])
@admin_required
def job_detail_route(job_id):
    response, status_code = get_job_detail(job_id)
    return jsonify(response), status_code


@admin_jobs_bp.route("/<int:job_id>/approve", methods=["PATCH"])
@admin_required
def approve_job_route(job_id):
    response, status_code = approve_job(job_id)
    return jsonify(response), status_code


@admin_jobs_bp.route("/<int:job_id>/reject", methods=["PATCH"])
@admin_required
def reject_job_route(job_id):
    data = request.get_json(silent=True) or {}
    response, status_code = reject_job(job_id, rejection_reason=data.get("rejection_reason"))
    return jsonify(response), status_code


@admin_jobs_bp.route("/<int:job_id>/close", methods=["PATCH"])
@admin_required
def close_job_route(job_id):
    response, status_code = close_job(job_id)
    return jsonify(response), status_code
