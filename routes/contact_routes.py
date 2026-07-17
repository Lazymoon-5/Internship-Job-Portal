from flask import Blueprint, request, jsonify
from controllers.contact_controller import submit_contact_form

contact_bp = Blueprint("contact_routes", __name__, url_prefix="/api/contact")


@contact_bp.route("", methods=["POST"])
def submit_contact_route():
    """
    POST /api/contact
    Public — no authentication. Powers the Landing Website's Contact page.
    Body: {name, email, message}  (also accepts "description" as an
    alias for "message", since that's what the page's field might be
    named on the frontend)
    """
    data = request.get_json(silent=True) or {}
    response, status_code = submit_contact_form(data)
    return jsonify(response), status_code
