from flask import Blueprint, request, jsonify
from controllers.admin_controller import login_admin, change_password
from config.jwt_auth import admin_required

admin_bp = Blueprint("admin_routes", __name__, url_prefix="/api/admin")


@admin_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    response, status_code = login_admin(data)
    return jsonify(response), status_code


@admin_bp.route("/change-password", methods=["POST"])
@admin_required
def change_password_route():
    data = request.get_json(silent=True) or {}
    # admin_id now comes from the verified JWT token (request.admin_id),
    # NOT from the request body — this closes the earlier security hole
    # where anyone could pass a different admin's ID.
    response, status_code = change_password(request.admin_id, data)
    return jsonify(response), status_code
