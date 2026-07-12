from flask import Blueprint, request, jsonify
from controllers.admin_report_controller import get_monthly_applications, get_status_breakdown
from config.jwt_auth import admin_required

admin_reports_bp = Blueprint("admin_reports_routes", __name__, url_prefix="/api/admin/reports")


@admin_reports_bp.route("/monthly-applications", methods=["GET"])
@admin_required
def monthly_applications_route():
    months_back = int(request.args.get("months", 6))
    response, status_code = get_monthly_applications(months_back)
    return jsonify(response), status_code


@admin_reports_bp.route("/status-breakdown", methods=["GET"])
@admin_required
def status_breakdown_route():
    response, status_code = get_status_breakdown()
    return jsonify(response), status_code
