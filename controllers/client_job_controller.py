"""
Client Job controller — Post a Job, Jobs Posted (Listing Management),
edit/close/mark-filled. This is the API that closes the long-standing
gap: companies can now actually create job posts through the app,
instead of only via the test-seed script.
"""

import models.job as job_model
import models.client as client_model
import models.notification as notification_model
import models.admin as admin_model


def _notify_admins_job_pending(client_id, job_title):
    """Best-effort broadcast to every admin — never blocks the job action itself."""
    try:
        client = client_model.find_by_id(client_id)
        company_name = client.company_name if client else "A company"
        for admin_id in admin_model.list_all_admin_ids():
            notification_model.create_notification(
                user_type="admin", user_id=admin_id,
                title="New Job Awaiting Approval",
                message=f'{company_name} submitted "{job_title}" for approval.',
            )
    except Exception as e:
        print(f"[NOTIFICATION] Failed to notify admins of pending job: {e}")


def post_job(client_id, data, submit_now=False):
    """
    submit_now=False -> saves as 'Draft' (matches "Save draft" button)
    submit_now=True  -> saves as 'Pending', awaiting Admin approval
                        (matches "Post Job" button)
    """
    title = (data.get("title") or "").strip()
    if not title:
        return {"success": False, "message": "Job title is required."}, 400

    required_skills = data.get("required_skills")
    if isinstance(required_skills, list):
        required_skills = ", ".join(required_skills)

    job_id = job_model.create_job({
        "client_id": client_id,
        "title": title,
        "description": data.get("description", ""),
        "job_type": data.get("job_type", "Internship"),
        "department": data.get("department", ""),
        "required_skills": required_skills or "",
        "eligibility_criteria": data.get("eligibility_criteria", ""),
        "location": data.get("location", ""),
        "salary_stipend": data.get("salary_stipend", ""),
        "last_date_to_apply": data.get("last_date_to_apply"),
    })

    if submit_now:
        job_model.update_job_status_by_client(job_id, client_id, "Pending")
        _notify_admins_job_pending(client_id, title)
        message = "Job submitted for admin approval."
    else:
        message = "Job saved as draft."

    return {"success": True, "message": message, "id": job_id}, 201


def safe_int(val, default=1):
    if val is None:
        return default
    try:
        val_str = str(val).strip()
        if not val_str or val_str in ("undefined", "null", "None"):
            return default
        return int(val_str)
    except (ValueError, TypeError):
        return default


def get_my_jobs(client_id, args):
    search = args.get("search", "").strip()
    status_filter = args.get("status", "").strip()
    page = safe_int(args.get("page"), 1)
    per_page = safe_int(args.get("per_page"), 10)

    jobs, total = job_model.list_jobs_by_client(client_id, search, status_filter, page, per_page)

    return {
        "success": True,
        "jobs": jobs,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if per_page else 1,
    }, 200


def get_my_jobs_stats(client_id):
    stats = job_model.get_client_job_stats(client_id)
    return {"success": True, "stats": stats}, 200


def get_my_job_detail(client_id, job_id):
    job = job_model.get_job_owned_by_client(job_id, client_id)
    if not job:
        return {"success": False, "message": "Job not found."}, 404
    return {"success": True, "job": job}, 200


def edit_job(client_id, job_id, data):
    job = job_model.get_job_owned_by_client(job_id, client_id)
    if not job:
        return {"success": False, "message": "Job not found."}, 404

    if job["status"] not in ("Draft", "Pending", "Rejected"):
        return {
            "success": False,
            "message": f"Cannot edit a job with status '{job['status']}'. Only Draft, Pending, or Rejected jobs can be edited."
        }, 400

    job_model.update_job(job_id, client_id, data)
    return {"success": True, "message": "Job updated."}, 200


def submit_job(client_id, job_id):
    """Moves a Draft job to Pending (awaiting admin approval)."""
    job = job_model.get_job_owned_by_client(job_id, client_id)
    if not job:
        return {"success": False, "message": "Job not found."}, 404

    if job["status"] != "Draft":
        return {"success": False, "message": "Only draft jobs can be submitted."}, 400

    job_model.update_job_status_by_client(job_id, client_id, "Pending")
    _notify_admins_job_pending(client_id, job["title"])
    return {"success": True, "message": "Job submitted for admin approval."}, 200


def close_job(client_id, job_id):
    job = job_model.get_job_owned_by_client(job_id, client_id)
    if not job:
        return {"success": False, "message": "Job not found."}, 404

    job_model.update_job_status_by_client(job_id, client_id, "Closed")
    return {"success": True, "message": "Job listing closed."}, 200


def mark_job_filled(client_id, job_id):
    job = job_model.get_job_owned_by_client(job_id, client_id)
    if not job:
        return {"success": False, "message": "Job not found."}, 404

    job_model.update_job_status_by_client(job_id, client_id, "Filled")
    return {"success": True, "message": "Job marked as filled."}, 200
