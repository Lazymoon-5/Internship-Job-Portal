from flask import Blueprint, request, jsonify
from controllers.admin_student_controller import (
    get_students, get_student_detail, block_student, unblock_student, delete_student_account
)
from config.jwt_auth import admin_required

admin_students_bp = Blueprint("admin_students_routes", __name__, url_prefix="/api/admin/students")


@admin_students_bp.route("", methods=["GET"])
@admin_required
def list_students_route():
    response, status_code = get_students(request.args)
    return jsonify(response), status_code


@admin_students_bp.route("/<int:student_id>", methods=["GET"])
@admin_required
def student_detail_route(student_id):
    response, status_code = get_student_detail(student_id)
    return jsonify(response), status_code


@admin_students_bp.route("/<int:student_id>/block", methods=["PATCH"])
@admin_required
def block_student_route(student_id):
    response, status_code = block_student(student_id)
    return jsonify(response), status_code


@admin_students_bp.route("/<int:student_id>/unblock", methods=["PATCH"])
@admin_required
def unblock_student_route(student_id):
    response, status_code = unblock_student(student_id)
    return jsonify(response), status_code


@admin_students_bp.route("/<int:student_id>", methods=["DELETE"])
@admin_required
def delete_student_route(student_id):
    response, status_code = delete_student_account(student_id)
    return jsonify(response), status_code
