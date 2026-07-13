import models.application as application_model


def get_applicants(client_id, job_id, args):
    search = args.get("search", "").strip()
    status_filter = args.get("status", "").strip()
    page = int(args.get("page", 1))
    per_page = int(args.get("per_page", 10))

    applications, total = application_model.list_applications_for_job(
        job_id, client_id, search, status_filter, page, per_page
    )

    if applications is None:
        return {"success": False, "message": "Job not found."}, 404

    return {
        "success": True,
        "applicants": applications,
        "total": total,
        "page": page,
        "per_page": per_page,
    }, 200


def get_applicant_stats(client_id, job_id):
    stats = application_model.get_job_applicant_stats(job_id, client_id)
    if stats is None:
        return {"success": False, "message": "Job not found."}, 404
    return {"success": True, "stats": stats}, 200


def get_applicant_profile(client_id, application_id):
    applicant = application_model.get_applicant_profile_for_client(application_id, client_id)
    if not applicant:
        return {"success": False, "message": "Applicant not found."}, 404
    return {"success": True, "applicant": applicant}, 200


def shortlist_applicant(client_id, application_id):
    updated = application_model.update_application_status_by_client(application_id, client_id, "Shortlisted")
    if not updated:
        return {"success": False, "message": "Applicant not found."}, 404
    return {"success": True, "message": "Candidate shortlisted."}, 200


def schedule_interview(client_id, application_id):
    updated = application_model.update_application_status_by_client(application_id, client_id, "Interview")
    if not updated:
        return {"success": False, "message": "Applicant not found."}, 404
    return {"success": True, "message": "Candidate moved to interview stage."}, 200


def extend_offer(client_id, application_id):
    updated = application_model.update_application_status_by_client(application_id, client_id, "Offered")
    if not updated:
        return {"success": False, "message": "Applicant not found."}, 404
    return {"success": True, "message": "Offer extended to candidate."}, 200


def reject_applicant(client_id, application_id):
    updated = application_model.update_application_status_by_client(application_id, client_id, "Rejected")
    if not updated:
        return {"success": False, "message": "Applicant not found."}, 404
    return {"success": True, "message": "Application rejected."}, 200
