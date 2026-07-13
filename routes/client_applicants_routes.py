from flask import Blueprint, request, jsonify
from controllers.client_applicant_controller import (
    get_applicants, get_applicant_stats, get_applicant_profile,
    shortlist_applicant, reject_applicant, schedule_interview, extend_offer
)
from config.jwt_auth import client_required

client_applicants_bp = Blueprint("client_applicants_routes", __name__, url_prefix="/api/client")


@client_applicants_bp.route("/jobs/<int:job_id>/applicants", methods=["GET"])
@client_required
def applicants_route(job_id):
    response, status_code = get_applicants(request.client_id, job_id, request.args)
    return jsonify(response), status_code


@client_applicants_bp.route("/jobs/<int:job_id>/applicants/stats", methods=["GET"])
@client_required
def applicant_stats_route(job_id):
    response, status_code = get_applicant_stats(request.client_id, job_id)
    return jsonify(response), status_code


@client_applicants_bp.route("/applicants/<int:application_id>", methods=["GET"])
@client_required
def applicant_profile_route(application_id):
    response, status_code = get_applicant_profile(request.client_id, application_id)
    return jsonify(response), status_code


@client_applicants_bp.route("/applicants/<int:application_id>/shortlist", methods=["PATCH"])
@client_required
def shortlist_route(application_id):
    response, status_code = shortlist_applicant(request.client_id, application_id)
    return jsonify(response), status_code


@client_applicants_bp.route("/applicants/<int:application_id>/reject", methods=["PATCH"])
@client_required
def reject_route(application_id):
    response, status_code = reject_applicant(request.client_id, application_id)
    return jsonify(response), status_code


@client_applicants_bp.route("/applicants/<int:application_id>/schedule-interview", methods=["PATCH"])
@client_required
def schedule_interview_route(application_id):
    response, status_code = schedule_interview(request.client_id, application_id)
    return jsonify(response), status_code


@client_applicants_bp.route("/applicants/<int:application_id>/extend-offer", methods=["PATCH"])
@client_required
def extend_offer_route(application_id):
    response, status_code = extend_offer(request.client_id, application_id)
    return jsonify(response), status_code
