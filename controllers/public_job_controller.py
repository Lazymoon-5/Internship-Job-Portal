"""
Public Jobs controller — no authentication required. Powers the
Home page's "Latest Jobs" preview and any public job browsing before
a student logs in. Only ever shows Admin-approved jobs, same rule as
the authenticated /api/student/jobs endpoint.
"""

import models.job as job_model


def browse_public_jobs(args):
    search = args.get("search", "").strip()
    job_type = args.get("job_type", "").strip()
    location = args.get("location", "").strip()
    page = int(args.get("page", 1))
    # "limit" is a convenience alias for per_page, since the Home page's
    # "Latest Jobs" preview naturally reads as "give me the latest N".
    per_page = int(args.get("limit") or args.get("per_page", 10))

    jobs, total = job_model.list_approved_jobs(search, job_type, location, page, per_page)

    return {
        "success": True,
        "jobs": jobs,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if per_page else 1,
    }, 200


def get_public_job_detail(job_id):
    job = job_model.get_approved_job_by_id(job_id)
    if not job:
        return {"success": False, "message": "Job not found."}, 404
    return {"success": True, "job": job}, 200
