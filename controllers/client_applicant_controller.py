import models.application as application_model
import models.client as client_model
import models.notification as notification_model
from config.email_service import send_recruiter_message_email


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


def _notify_student_status_change(application_id, title, message_template):
    """Best-effort — never blocks the actual status change if this fails."""
    try:
        info = application_model.get_student_and_job_for_application(application_id)
        if info:
            notification_model.create_notification(
                user_type="student",
                user_id=info["student_id"],
                title=title,
                message=message_template.format(job_title=info["job_title"]),
            )
    except Exception as e:
        print(f"[NOTIFICATION] Failed to notify student for application {application_id}: {e}")


def shortlist_applicant(client_id, application_id):
    updated = application_model.update_application_status_by_client(application_id, client_id, "Shortlisted")
    if not updated:
        return {"success": False, "message": "Applicant not found."}, 404

    _notify_student_status_change(
        application_id, "Application Shortlisted",
        "Good news! You've been shortlisted for {job_title}."
    )
    return {"success": True, "message": "Candidate shortlisted."}, 200


def schedule_interview(client_id, application_id):
    updated = application_model.update_application_status_by_client(application_id, client_id, "Interview")
    if not updated:
        return {"success": False, "message": "Applicant not found."}, 404

    _notify_student_status_change(
        application_id, "Interview Scheduled",
        "You've been moved to the interview stage for {job_title}."
    )
    return {"success": True, "message": "Candidate moved to interview stage."}, 200


def extend_offer(client_id, application_id):
    updated = application_model.update_application_status_by_client(application_id, client_id, "Offered")
    if not updated:
        return {"success": False, "message": "Applicant not found."}, 404

    _notify_student_status_change(
        application_id, "Offer Received!",
        "Congratulations! You've received an offer for {job_title}."
    )
    return {"success": True, "message": "Offer extended to candidate."}, 200


def reject_applicant(client_id, application_id):
    updated = application_model.update_application_status_by_client(application_id, client_id, "Rejected")
    if not updated:
        return {"success": False, "message": "Applicant not found."}, 404

    _notify_student_status_change(
        application_id, "Application Update",
        "Your application for {job_title} was not successful this time."
    )
    return {"success": True, "message": "Application rejected."}, 200


def message_all_applicants(client_id, job_id, data):
    """
    Sends a real email (via Resend) to every applicant of this job.
    Returns a per-recipient success count rather than a single
    true/false, since individual emails can fail independently
    (e.g. one bad address shouldn't block the rest from sending).
    """
    subject = (data.get("subject") or "").strip()
    message = (data.get("message") or "").strip()

    if not subject or not message:
        return {"success": False, "message": "subject and message are both required."}, 400

    recipients = application_model.get_applicant_emails_for_job(job_id, client_id)
    if recipients is None:
        return {"success": False, "message": "Job not found."}, 404

    if not recipients:
        return {"success": False, "message": "No applicants to message for this job yet."}, 400

    client = client_model.find_by_id(client_id)
    company_name = client.company_name if client else "A company on Placify"

    sent_count = 0
    failed_count = 0
    for recipient in recipients:
        success = send_recruiter_message_email(
            recipient["student_email"], company_name, subject, message
        )
        if success:
            sent_count += 1
        else:
            failed_count += 1

    return {
        "success": True,
        "message": f"Message sent to {sent_count} of {len(recipients)} applicant(s).",
        "sent_count": sent_count,
        "failed_count": failed_count,
        "total_recipients": len(recipients),
    }, 200
