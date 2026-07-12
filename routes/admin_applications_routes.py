from flask import Blueprint, request, jsonify
from controllers.admin_application_controller import (
    get_applications, get_application_stats, get_application_detail,
    shortlist_application, reject_application
)
from config.jwt_auth import admin_required

admin_applications_bp = Blueprint("admin_applications_routes", __name__, url_prefix="/api/admin/applications")


@admin_applications_bp.route("", methods=["GET"])
@admin_required
def list_applications_route():
    response, status_code = get_applications(request.args)
    return jsonify(response), status_code


@admin_applications_bp.route("/stats", methods=["GET"])
@admin_required
def application_stats_route():
    response, status_code = get_application_stats()
    return jsonify(response), status_code


@admin_applications_bp.route("/<int:application_id>", methods=["GET"])
@admin_required
def application_detail_route(application_id):
    response, status_code = get_application_detail(application_id)
    return jsonify(response), status_code


@admin_applications_bp.route("/<int:application_id>/shortlist", methods=["PATCH"])
@admin_required
def shortlist_application_route(application_id):
    data = request.get_json(silent=True) or {}
    response, status_code = shortlist_application(application_id, data.get("admin_notes"))
    return jsonify(response), status_code


@admin_applications_bp.route("/<int:application_id>/reject", methods=["PATCH"])
@admin_required
def reject_application_route(application_id):
    data = request.get_json(silent=True) or {}
    response, status_code = reject_application(application_id, data.get("admin_notes"))
    return jsonify(response), status_code
