from flask import Blueprint, request, jsonify
from controllers.client_job_controller import (
    post_job, get_my_jobs, get_my_jobs_stats, get_my_job_detail,
    edit_job, submit_job, close_job, mark_job_filled
)
from config.jwt_auth import client_required

client_jobs_bp = Blueprint("client_jobs_routes", __name__, url_prefix="/api/client/jobs")


@client_jobs_bp.route("", methods=["POST"])
@client_required
def post_job_route():
    data = request.get_json(silent=True) or {}
    submit_now = data.pop("submit_now", False)
    response, status_code = post_job(request.client_id, data, submit_now)
    return jsonify(response), status_code


@client_jobs_bp.route("", methods=["GET"])
@client_required
def my_jobs_route():
    response, status_code = get_my_jobs(request.client_id, request.args)
    return jsonify(response), status_code


@client_jobs_bp.route("/stats", methods=["GET"])
@client_required
def my_jobs_stats_route():
    response, status_code = get_my_jobs_stats(request.client_id)
    return jsonify(response), status_code


@client_jobs_bp.route("/<int:job_id>", methods=["GET"])
@client_required
def my_job_detail_route(job_id):
    response, status_code = get_my_job_detail(request.client_id, job_id)
    return jsonify(response), status_code


@client_jobs_bp.route("/<int:job_id>", methods=["PUT"])
@client_required
def edit_job_route(job_id):
    data = request.get_json(silent=True) or {}
    response, status_code = edit_job(request.client_id, job_id, data)
    return jsonify(response), status_code


@client_jobs_bp.route("/<int:job_id>/submit", methods=["PATCH"])
@client_required
def submit_job_route(job_id):
    response, status_code = submit_job(request.client_id, job_id)
    return jsonify(response), status_code


@client_jobs_bp.route("/<int:job_id>/close", methods=["PATCH"])
@client_required
def close_job_route(job_id):
    response, status_code = close_job(request.client_id, job_id)
    return jsonify(response), status_code


@client_jobs_bp.route("/<int:job_id>/mark-filled", methods=["PATCH"])
@client_required
def mark_filled_route(job_id):
    response, status_code = mark_job_filled(request.client_id, job_id)
    return jsonify(response), status_code
