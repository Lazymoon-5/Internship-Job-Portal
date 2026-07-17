from flask import Blueprint, request, jsonify
from controllers.client_notification_controller import (
    get_notifications, mark_all_notifications_read, mark_notification_read
)
from config.jwt_auth import client_required

client_notifications_bp = Blueprint("client_notifications_routes", __name__, url_prefix="/api/client/notifications")


@client_notifications_bp.route("", methods=["GET"])
@client_required
def list_notifications_route():
    response, status_code = get_notifications(request.client_id, request.args)
    return jsonify(response), status_code


@client_notifications_bp.route("/mark-all-read", methods=["PATCH"])
@client_required
def mark_all_read_route():
    response, status_code = mark_all_notifications_read(request.client_id)
    return jsonify(response), status_code


@client_notifications_bp.route("/<int:notification_id>/mark-read", methods=["PATCH"])
@client_required
def mark_one_read_route(notification_id):
    response, status_code = mark_notification_read(notification_id)
    return jsonify(response), status_code
