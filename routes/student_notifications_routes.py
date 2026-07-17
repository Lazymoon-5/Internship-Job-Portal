from flask import Blueprint, request, jsonify
from controllers.student_notification_controller import (
    get_notifications, mark_all_notifications_read, mark_notification_read
)
from config.jwt_auth import student_required

student_notifications_bp = Blueprint("student_notifications_routes", __name__, url_prefix="/api/student/notifications")


@student_notifications_bp.route("", methods=["GET"])
@student_required
def list_notifications_route():
    response, status_code = get_notifications(request.student_id, request.args)
    return jsonify(response), status_code


@student_notifications_bp.route("/mark-all-read", methods=["PATCH"])
@student_required
def mark_all_read_route():
    response, status_code = mark_all_notifications_read(request.student_id)
    return jsonify(response), status_code


@student_notifications_bp.route("/<int:notification_id>/mark-read", methods=["PATCH"])
@student_required
def mark_one_read_route(notification_id):
    response, status_code = mark_notification_read(notification_id)
    return jsonify(response), status_code
