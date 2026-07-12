from flask import Blueprint, request, jsonify
from controllers.admin_notification_controller import (
    get_notifications, mark_all_notifications_read, mark_notification_read
)
from config.jwt_auth import admin_required

admin_notifications_bp = Blueprint("admin_notifications_routes", __name__, url_prefix="/api/admin/notifications")


@admin_notifications_bp.route("", methods=["GET"])
@admin_required
def list_notifications_route():
    # admin_id now comes from the verified JWT token, not a query param
    # someone could otherwise tamper with to read another admin's notifications.
    response, status_code = get_notifications(request.admin_id, request.args)
    return jsonify(response), status_code


@admin_notifications_bp.route("/mark-all-read", methods=["PATCH"])
@admin_required
def mark_all_read_route():
    response, status_code = mark_all_notifications_read(request.admin_id)
    return jsonify(response), status_code


@admin_notifications_bp.route("/<int:notification_id>/mark-read", methods=["PATCH"])
@admin_required
def mark_one_read_route(notification_id):
    response, status_code = mark_notification_read(notification_id)
    return jsonify(response), status_code
