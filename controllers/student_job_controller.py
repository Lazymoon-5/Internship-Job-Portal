import models.job as job_model


def browse_jobs(args):
    search = args.get("search", "").strip()
    job_type = args.get("job_type", "").strip()
    location = args.get("location", "").strip()
    page = int(args.get("page", 1))
    per_page = int(args.get("per_page", 10))

    jobs, total = job_model.list_approved_jobs(search, job_type, location, page, per_page)

    return {
        "success": True,
        "jobs": jobs,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if per_page else 1,
    }, 200


def get_job_detail(job_id):
    job = job_model.get_approved_job_by_id(job_id)
    if not job:
        return {"success": False, "message": "Job not found."}, 404
    return {"success": True, "job": job}, 200
