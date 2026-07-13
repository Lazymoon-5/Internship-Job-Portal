from flask import Blueprint, request, jsonify
from controllers.client_dashboard_controller import get_dashboard_stats, get_recent_applications, get_active_jobs
from config.jwt_auth import client_required

client_dashboard_bp = Blueprint("client_dashboard_routes", __name__, url_prefix="/api/client/dashboard")


@client_dashboard_bp.route("/stats", methods=["GET"])
@client_required
def stats_route():
    response, status_code = get_dashboard_stats(request.client_id)
    return jsonify(response), status_code


@client_dashboard_bp.route("/recent-applications", methods=["GET"])
@client_required
def recent_applications_route():
    response, status_code = get_recent_applications(request.client_id)
    return jsonify(response), status_code


@client_dashboard_bp.route("/active-jobs", methods=["GET"])
@client_required
def active_jobs_route():
    response, status_code = get_active_jobs(request.client_id)
    return jsonify(response), status_code
