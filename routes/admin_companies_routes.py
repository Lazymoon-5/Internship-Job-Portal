from flask import Blueprint, request, jsonify
from controllers.admin_client_controller import (
    get_companies, get_company_detail, approve_company, reject_company,
    block_company, delete_company_account
)
from config.jwt_auth import admin_required

admin_companies_bp = Blueprint("admin_companies_routes", __name__, url_prefix="/api/admin/companies")


@admin_companies_bp.route("", methods=["GET"])
@admin_required
def list_companies_route():
    response, status_code = get_companies(request.args)
    return jsonify(response), status_code


@admin_companies_bp.route("/<int:client_id>", methods=["GET"])
@admin_required
def company_detail_route(client_id):
    response, status_code = get_company_detail(client_id)
    return jsonify(response), status_code


@admin_companies_bp.route("/<int:client_id>/approve", methods=["PATCH"])
@admin_required
def approve_company_route(client_id):
    response, status_code = approve_company(client_id)
    return jsonify(response), status_code


@admin_companies_bp.route("/<int:client_id>/reject", methods=["PATCH"])
@admin_required
def reject_company_route(client_id):
    response, status_code = reject_company(client_id)
    return jsonify(response), status_code


@admin_companies_bp.route("/<int:client_id>/block", methods=["PATCH"])
@admin_required
def block_company_route(client_id):
    response, status_code = block_company(client_id)
    return jsonify(response), status_code


@admin_companies_bp.route("/<int:client_id>", methods=["DELETE"])
@admin_required
def delete_company_route(client_id):
    response, status_code = delete_company_account(client_id)
    return jsonify(response), status_code
