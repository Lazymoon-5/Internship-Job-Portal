"""
Manage Job Posts controller — list/search/filter, approve/reject,
plus the stat cards shown at the top of that page (Total Posts,
Pending Review, Active Jobs, Total Applications).
"""

from config.database import is_db_available
import models.job as job_model


def get_jobs(args):
    if not is_db_available():
        return {
            "success": True, "jobs": [], "total": 0, "page": 1, "per_page": 10, "total_pages": 0,
            "message": "Database not connected — job listings require a real database."
        }, 200

    search = args.get("search", "").strip()
    status_filter = args.get("status", "").strip()
    page = int(args.get("page", 1))
    per_page = int(args.get("per_page", 10))

    jobs, total = job_model.list_jobs(search, status_filter, page, per_page)

    return {
        "success": True,
        "jobs": jobs,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if per_page else 1,
    }, 200


def get_job_moderation_stats():
    if not is_db_available():
        return {
            "success": True,
            "stats": {"total_posts": 0, "pending_review": 0, "active_jobs": 0, "total_applications": 0},
            "message": "Database not connected."
        }, 200

    import models.application as application_model
    return {
        "success": True,
        "stats": {
            "total_posts": job_model.count_jobs(),
            "pending_review": job_model.count_jobs_by_status("Pending"),
            "active_jobs": job_model.count_jobs_by_status("Approved"),
            "total_applications": application_model.count_applications(),
        }
    }, 200


def get_job_detail(job_id):
    job = job_model.get_job_by_id(job_id)
    if not job:
        return {"success": False, "message": "Job post not found."}, 404
    return {"success": True, "job": job}, 200


def approve_job(job_id):
    job = job_model.get_job_by_id(job_id)
    if not job:
        return {"success": False, "message": "Job post not found."}, 404

    job_model.update_job_status(job_id, "Approved")
    return {"success": True, "message": "Job post approved and now visible to students."}, 200


def reject_job(job_id):
    job = job_model.get_job_by_id(job_id)
    if not job:
        return {"success": False, "message": "Job post not found."}, 404

    job_model.update_job_status(job_id, "Rejected")
    return {"success": True, "message": "Job post rejected."}, 200


def close_job(job_id):
    job = job_model.get_job_by_id(job_id)
    if not job:
        return {"success": False, "message": "Job post not found."}, 404

    job_model.update_job_status(job_id, "Closed")
    return {"success": True, "message": "Job post closed."}, 200
