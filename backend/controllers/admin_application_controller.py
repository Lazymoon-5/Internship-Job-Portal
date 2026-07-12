"""
Manage Applications controller — list/search/filter, plus the
Application Detail page (full applicant dossier) with Shortlist/Reject
actions.
"""

from config.database import is_db_available
import models.application as application_model


def get_applications(args):
    if not is_db_available():
        return {
            "success": True, "applications": [], "total": 0, "page": 1, "per_page": 10, "total_pages": 0,
            "message": "Database not connected — application listings require a real database."
        }, 200

    search = args.get("search", "").strip()
    status_filter = args.get("status", "").strip()
    page = int(args.get("page", 1))
    per_page = int(args.get("per_page", 10))

    applications, total = application_model.list_applications(search, status_filter, page, per_page)

    return {
        "success": True,
        "applications": applications,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if per_page else 1,
    }, 200


def get_application_stats():
    if not is_db_available():
        return {
            "success": True,
            "stats": {"total_applied": 0, "pending_review": 0, "shortlisted": 0, "rejected": 0},
            "message": "Database not connected."
        }, 200

    return {
        "success": True,
        "stats": {
            "total_applied": application_model.count_applications(),
            "pending_review": application_model.count_applications_by_status("Applied")
                             + application_model.count_applications_by_status("In Review"),
            "shortlisted": application_model.count_applications_by_status("Shortlisted"),
            "rejected": application_model.count_applications_by_status("Rejected"),
        }
    }, 200


def get_application_detail(application_id):
    application = application_model.get_application_by_id(application_id)
    if not application:
        return {"success": False, "message": "Application not found."}, 404
    return {"success": True, "application": application}, 200


def shortlist_application(application_id, admin_notes=None):
    application = application_model.get_application_by_id(application_id)
    if not application:
        return {"success": False, "message": "Application not found."}, 404

    application_model.update_application_status(application_id, "Shortlisted", admin_notes)
    return {"success": True, "message": "Candidate shortlisted."}, 200


def reject_application(application_id, admin_notes=None):
    application = application_model.get_application_by_id(application_id)
    if not application:
        return {"success": False, "message": "Application not found."}, 404

    application_model.update_application_status(application_id, "Rejected", admin_notes)
    return {"success": True, "message": "Application rejected."}, 200
