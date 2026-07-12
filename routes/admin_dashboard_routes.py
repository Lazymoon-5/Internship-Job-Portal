from flask import Blueprint, jsonify
from controllers.admin_dashboard_controller import get_dashboard_stats, get_recent_applications
from config.jwt_auth import admin_required

admin_dashboard_bp = Blueprint("admin_dashboard_routes", __name__, url_prefix="/api/admin/dashboard")


@admin_dashboard_bp.route("/stats", methods=["GET"])
@admin_required
def stats():
    response, status_code = get_dashboard_stats()
    return jsonify(response), status_code


@admin_dashboard_bp.route("/recent-applications", methods=["GET"])
@admin_required
def recent_applications():
    response, status_code = get_recent_applications()
    return jsonify(response), status_code
