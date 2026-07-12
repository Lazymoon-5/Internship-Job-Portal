import models.application as application_model
import models.resume as resume_model


def apply_to_job(student_id, job_id, data):
    cover_letter = data.get("cover_letter", "")
    portfolio_link = data.get("portfolio_link", "")
    resume_id = data.get("resume_id")

    # If no specific resume was chosen, default to the student's primary one
    if not resume_id:
        primary = resume_model.get_primary_resume(student_id)
        resume_id = primary["id"] if primary else None

    if not resume_id:
        return {
            "success": False,
            "message": "Please upload a resume before applying — no resume found on your profile."
        }, 400

    new_id, error = application_model.create_application_with_check(
        student_id, job_id, cover_letter, portfolio_link, resume_id
    )

    if error:
        status_code = 409 if "already applied" in error else 400
        return {"success": False, "message": error}, status_code

    return {"success": True, "message": "Application submitted successfully.", "id": new_id}, 201


def get_my_applications(student_id, args):
    page = int(args.get("page", 1))
    per_page = int(args.get("per_page", 20))

    applications, total = application_model.list_applications_by_student(student_id, page, per_page)

    return {
        "success": True,
        "applications": applications,
        "total": total,
        "page": page,
        "per_page": per_page,
    }, 200


def get_my_application_stats(student_id):
    stats = application_model.get_student_application_stats(student_id)
    return {"success": True, "stats": stats}, 200


def get_my_application_detail(student_id, application_id):
    application = application_model.get_student_application_detail(application_id, student_id)
    if not application:
        return {"success": False, "message": "Application not found."}, 404
    return {"success": True, "application": application}, 200
