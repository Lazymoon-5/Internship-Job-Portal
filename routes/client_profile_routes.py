from flask import Blueprint, request, jsonify
from controllers.client_profile_controller import get_profile, update_profile
from config.jwt_auth import client_required

client_profile_bp = Blueprint("client_profile_routes", __name__, url_prefix="/api/client/profile")


@client_profile_bp.route("", methods=["GET"])
@client_required
def get_profile_route():
    response, status_code = get_profile(request.client_id)
    return jsonify(response), status_code


@client_profile_bp.route("", methods=["PUT"])
@client_required
def update_profile_route():
    data = request.get_json(silent=True) or {}
    mark_completed = data.pop("mark_completed", False)
    response, status_code = update_profile(request.client_id, data, mark_completed)
    return jsonify(response), status_code
