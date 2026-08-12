import models.application as application_model
import models.resume as resume_model
import models.job as job_model
import models.student as student_model
import models.student_profile as student_profile_model
import models.client as client_model
import models.notification as notification_model
from config.email_service import send_application_confirmation_email, send_new_applicant_email


def apply_to_job(student_id, job_id, data):
    # Enforce student profile completion (min 90%)
    profile = student_profile_model.get_profile(student_id)
    if profile:
        completion = profile.get("profile_completion", 0)
        if completion < 90:
            return {
                "success": False,
                "message": f"Complete your profile to apply for Jobs (at least 90% completion required, current: {completion}%)."
            }, 400

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

    # Notify + email the company that owns this job, and email the
    # student a confirmation — all best-effort, never blocks the
    # application itself if something here fails.
    try:
        job = job_model.get_job_by_id(job_id)
        student = student_model.find_by_id(student_id)
        if job and student:
            company_name = job.get("company_name", "the company")

            notification_model.create_notification(
                user_type="client",
                user_id=job["client_id"],
                title="New Application Received",
                message=f"{student.name} applied for {job['title']}.",
            )

            # E1 — confirmation email to the student
            send_application_confirmation_email(
                student.email, new_id, job["title"], company_name,
                applied_date=__import__("datetime").datetime.utcnow().strftime("%B %d, %Y"),
                status="Applied",
            )

            # E2 — new applicant alert to the company
            client = client_model.find_by_id(job["client_id"])
            if client:
                send_new_applicant_email(client.email, company_name, student.name, job["title"])

    except Exception as e:
        print(f"[NOTIFICATION/EMAIL] Failed during post-application hooks: {e}")

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
