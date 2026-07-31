from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

from api.utils import parse_request_data, json_response
from config.jwt_auth import admin_required, student_required, client_required

# Controller imports
from controllers.student_controller import (
    register_student,
    login_student,
    verify_registration_otp as verify_student_otp,
    resend_otp as resend_student_otp,
    google_login,
    forgot_password as student_forgot_pw,
    reset_password as student_reset_pw,
    change_password as student_change_pw,
)
from controllers.student_profile_controller import (
    get_profile as get_student_profile,
    update_profile as update_student_profile,
    update_profile_photo,
    add_certification,
    delete_certification,
    add_skill,
    delete_skill,
)
from controllers.student_resume_controller import (
    get_resumes,
    add_resume,
    set_primary_resume,
    delete_resume,
)
from controllers.student_job_controller import (
    browse_jobs,
    get_job_detail as get_student_job_detail,
)
from controllers.student_application_controller import (
    apply_to_job,
    get_my_applications,
    get_my_application_stats,
    get_my_application_detail,
)
from controllers.student_notification_controller import (
    get_notifications as get_student_notifications,
    mark_all_notifications_read as mark_all_student_notifications_read,
    mark_notification_read as mark_student_notification_read,
)
from controllers.client_controller import (
    register_client,
    login_client,
    verify_registration_otp as verify_client_otp,
    resend_otp as resend_client_otp,
    forgot_password as client_forgot_pw,
    reset_password as client_reset_pw,
    change_password as client_change_pw,
)
from controllers.client_dashboard_controller import (
    get_dashboard_stats as get_client_dashboard_stats,
    get_recent_applications as get_client_recent_applications,
    get_active_jobs as get_client_active_jobs,
)
from controllers.client_profile_controller import (
    get_profile as get_client_profile,
    update_profile as update_client_profile,
)
from controllers.client_job_controller import (
    post_job,
    get_my_jobs,
    get_my_jobs_stats,
    get_my_job_detail,
    edit_job,
    submit_job,
    close_job as close_client_job,
    mark_job_filled,
)
from controllers.client_applicant_controller import (
    get_applicants,
    get_applicant_stats,
    get_applicant_profile,
    shortlist_applicant,
    reject_applicant,
    schedule_interview,
    extend_offer,
    message_all_applicants,
)
from controllers.client_notification_controller import (
    get_notifications as get_client_notifications,
    mark_all_notifications_read as mark_all_client_notifications_read,
    mark_notification_read as mark_client_notification_read,
)
from controllers.admin_controller import (
    login_admin,
    change_password as admin_change_pw,
)
from controllers.admin_dashboard_controller import (
    get_dashboard_stats as get_admin_dashboard_stats,
    get_recent_applications as get_admin_recent_applications,
)
from controllers.admin_student_controller import (
    get_students as get_admin_students,
    get_student_detail as get_admin_student_detail,
    block_student,
    unblock_student,
    delete_student_account,
)
from controllers.admin_client_controller import (
    get_companies,
    get_company_detail,
    approve_company,
    reject_company,
    block_company,
    delete_company_account,
)
from controllers.admin_job_controller import (
    get_jobs as get_admin_jobs,
    get_job_moderation_stats as get_admin_job_stats,
    get_job_detail as get_admin_job_detail,
    approve_job as admin_approve_job,
    reject_job as admin_reject_job,
    close_job as admin_close_job,
)
from controllers.admin_application_controller import (
    get_applications as get_admin_applications,
    get_application_stats as get_admin_app_stats,
    get_application_detail as get_admin_app_detail,
    shortlist_application as admin_shortlist_app,
    reject_application as admin_reject_app,
)
from controllers.admin_report_controller import (
    get_monthly_applications,
    get_status_breakdown,
)
from controllers.admin_notification_controller import (
    get_notifications as get_admin_notifications,
    mark_all_notifications_read as mark_all_admin_notifications_read,
    mark_notification_read as mark_admin_notification_read,
)
from controllers.public_job_controller import (
    browse_public_jobs,
    get_public_job_detail,
)
from controllers.contact_controller import submit_contact_form


# ==========================================
# STUDENT VIEWS
# ==========================================

@csrf_exempt
def api_student_register(request):
    data = parse_request_data(request)
    return json_response(register_student(data))

@csrf_exempt
def api_student_login(request):
    data = parse_request_data(request)
    return json_response(login_student(data))

@csrf_exempt
def api_student_verify_otp(request):
    data = parse_request_data(request)
    return json_response(verify_student_otp(data))

@csrf_exempt
def api_student_resend_otp(request):
    data = parse_request_data(request)
    return json_response(resend_student_otp(data))

@csrf_exempt
def api_student_google_login(request):
    data = parse_request_data(request)
    return json_response(google_login(data))

@csrf_exempt
def api_student_forgot_password(request):
    data = parse_request_data(request)
    return json_response(student_forgot_pw(data))

@csrf_exempt
def api_student_reset_password(request):
    data = parse_request_data(request)
    return json_response(student_reset_pw(data))

@csrf_exempt
@student_required
def api_student_change_password(request):
    data = parse_request_data(request)
    return json_response(student_change_pw(request.student_id, data))

@csrf_exempt
@student_required
def api_student_profile(request):
    if request.method == "GET":
        return json_response(get_student_profile(request.student_id))
    elif request.method in ("PUT", "POST"):
        data = parse_request_data(request)
        mark_completed = request.GET.get("completed", "").lower() == "true" or data.get("completed") is True
        return json_response(update_student_profile(request.student_id, data, mark_completed=mark_completed))
    return json_response({"success": False, "message": "Method not allowed"}, status=405)

@csrf_exempt
@student_required
def api_student_profile_photo(request):
    data = parse_request_data(request)
    return json_response(update_profile_photo(request.student_id, data))

@csrf_exempt
@student_required
def api_student_certifications(request):
    data = parse_request_data(request)
    return json_response(add_certification(request.student_id, data))

@csrf_exempt
@student_required
def api_student_delete_certification(request, certification_id):
    return json_response(delete_certification(request.student_id, int(certification_id)))

@csrf_exempt
@student_required
def api_student_skills(request):
    data = parse_request_data(request)
    return json_response(add_skill(request.student_id, data))

@csrf_exempt
@student_required
def api_student_delete_skill(request, skill_id):
    return json_response(delete_skill(request.student_id, int(skill_id)))

@csrf_exempt
@student_required
def api_student_resumes(request):
    if request.method == "GET":
        return json_response(get_resumes(request.student_id))
    elif request.method == "POST":
        data = parse_request_data(request)
        return json_response(add_resume(request.student_id, data))
    return json_response({"success": False, "message": "Method not allowed"}, status=405)

@csrf_exempt
@student_required
def api_student_set_primary_resume(request, resume_id):
    return json_response(set_primary_resume(request.student_id, int(resume_id)))

@csrf_exempt
@student_required
def api_student_delete_resume(request, resume_id):
    return json_response(delete_resume(request.student_id, int(resume_id)))

@csrf_exempt
@student_required
def api_student_jobs(request):
    args = parse_request_data(request)
    return json_response(browse_jobs(args))

@csrf_exempt
@student_required
def api_student_job_detail(request, job_id):
    return json_response(get_student_job_detail(int(job_id)))

@csrf_exempt
@student_required
def api_student_apply_job(request, job_id):
    data = parse_request_data(request)
    return json_response(apply_to_job(request.student_id, int(job_id), data))

@csrf_exempt
@student_required
def api_student_applications(request):
    args = parse_request_data(request)
    return json_response(get_my_applications(request.student_id, args))

@csrf_exempt
@student_required
def api_student_applications_stats(request):
    return json_response(get_my_application_stats(request.student_id))

@csrf_exempt
@student_required
def api_student_application_detail(request, application_id):
    return json_response(get_my_application_detail(request.student_id, int(application_id)))

@csrf_exempt
@student_required
def api_student_notifications(request):
    args = parse_request_data(request)
    return json_response(get_student_notifications(request.student_id, args))

@csrf_exempt
@student_required
def api_student_notifications_mark_all_read(request):
    return json_response(mark_all_student_notifications_read(request.student_id))

@csrf_exempt
@student_required
def api_student_notification_mark_read(request, notification_id):
    return json_response(mark_student_notification_read(int(notification_id)))


# ==========================================
# CLIENT (COMPANY) VIEWS
# ==========================================

@csrf_exempt
def api_client_register(request):
    data = parse_request_data(request)
    return json_response(register_client(data))

@csrf_exempt
def api_client_login(request):
    data = parse_request_data(request)
    return json_response(login_client(data))

@csrf_exempt
def api_client_verify_otp(request):
    data = parse_request_data(request)
    return json_response(verify_client_otp(data))

@csrf_exempt
def api_client_resend_otp(request):
    data = parse_request_data(request)
    return json_response(resend_client_otp(data))

@csrf_exempt
def api_client_forgot_password(request):
    data = parse_request_data(request)
    return json_response(client_forgot_pw(data))

@csrf_exempt
def api_client_reset_password(request):
    data = parse_request_data(request)
    return json_response(client_reset_pw(data))

@csrf_exempt
@client_required
def api_client_change_password(request):
    data = parse_request_data(request)
    return json_response(client_change_pw(request.client_id, data))

@csrf_exempt
@client_required
def api_client_dashboard_stats(request):
    return json_response(get_client_dashboard_stats(request.client_id))

@csrf_exempt
@client_required
def api_client_dashboard_recent_applications(request):
    return json_response(get_client_recent_applications(request.client_id))

@csrf_exempt
@client_required
def api_client_dashboard_active_jobs(request):
    return json_response(get_client_active_jobs(request.client_id))

@csrf_exempt
@client_required
def api_client_profile(request):
    if request.method == "GET":
        return json_response(get_client_profile(request.client_id))
    elif request.method in ("PUT", "POST"):
        data = parse_request_data(request)
        mark_completed = request.GET.get("completed", "").lower() == "true" or data.get("completed") is True
        return json_response(update_client_profile(request.client_id, data, mark_completed=mark_completed))
    return json_response({"success": False, "message": "Method not allowed"}, status=405)

@csrf_exempt
@client_required
def api_client_jobs(request):
    if request.method == "GET":
        args = parse_request_data(request)
        return json_response(get_my_jobs(request.client_id, args))
    elif request.method == "POST":
        data = parse_request_data(request)
        submit_now = data.pop("submit_now", False)
        return json_response(post_job(request.client_id, data, submit_now))
    return json_response({"success": False, "message": "Method not allowed"}, status=405)

@csrf_exempt
@client_required
def api_client_jobs_stats(request):
    return json_response(get_my_jobs_stats(request.client_id))

@csrf_exempt
@client_required
def api_client_job_detail(request, job_id):
    job_id = int(job_id)
    if request.method == "GET":
        return json_response(get_my_job_detail(request.client_id, job_id))
    elif request.method in ("PUT", "POST"):
        data = parse_request_data(request)
        return json_response(edit_job(request.client_id, job_id, data))
    return json_response({"success": False, "message": "Method not allowed"}, status=405)

@csrf_exempt
@client_required
def api_client_job_submit(request, job_id):
    return json_response(submit_job(request.client_id, int(job_id)))

@csrf_exempt
@client_required
def api_client_job_close(request, job_id):
    return json_response(close_client_job(request.client_id, int(job_id)))

@csrf_exempt
@client_required
def api_client_job_mark_filled(request, job_id):
    return json_response(mark_job_filled(request.client_id, int(job_id)))

@csrf_exempt
@client_required
def api_client_job_applicants(request, job_id):
    args = parse_request_data(request)
    return json_response(get_applicants(request.client_id, int(job_id), args))

@csrf_exempt
@client_required
def api_client_job_applicants_stats(request, job_id):
    return json_response(get_applicant_stats(request.client_id, int(job_id)))

@csrf_exempt
@client_required
def api_client_applicant_detail(request, application_id):
    return json_response(get_applicant_profile(request.client_id, int(application_id)))

@csrf_exempt
@client_required
def api_client_applicant_shortlist(request, application_id):
    return json_response(shortlist_applicant(request.client_id, int(application_id)))

@csrf_exempt
@client_required
def api_client_applicant_reject(request, application_id):
    return json_response(reject_applicant(request.client_id, int(application_id)))

@csrf_exempt
@client_required
def api_client_applicant_schedule_interview(request, application_id):
    return json_response(schedule_interview(request.client_id, int(application_id)))

@csrf_exempt
@client_required
def api_client_applicant_extend_offer(request, application_id):
    return json_response(extend_offer(request.client_id, int(application_id)))

@csrf_exempt
@client_required
def api_client_job_message_applicants(request, job_id):
    data = parse_request_data(request)
    return json_response(message_all_applicants(request.client_id, int(job_id), data))

@csrf_exempt
@client_required
def api_client_notifications(request):
    args = parse_request_data(request)
    return json_response(get_client_notifications(request.client_id, args))

@csrf_exempt
@client_required
def api_client_notifications_mark_all_read(request):
    return json_response(mark_all_client_notifications_read(request.client_id))

@csrf_exempt
@client_required
def api_client_notification_mark_read(request, notification_id):
    return json_response(mark_client_notification_read(int(notification_id)))


# ==========================================
# ADMIN VIEWS
# ==========================================

@csrf_exempt
def api_admin_login(request):
    data = parse_request_data(request)
    return json_response(login_admin(data))

@csrf_exempt
@admin_required
def api_admin_change_password(request):
    data = parse_request_data(request)
    return json_response(admin_change_pw(request.admin_id, data))

@csrf_exempt
@admin_required
def api_admin_dashboard_stats(request):
    return json_response(get_admin_dashboard_stats())

@csrf_exempt
@admin_required
def api_admin_dashboard_recent_applications(request):
    return json_response(get_admin_recent_applications())

@csrf_exempt
@admin_required
def api_admin_students(request):
    args = parse_request_data(request)
    return json_response(get_admin_students(args))

@csrf_exempt
@admin_required
def api_admin_student_detail(request, student_id):
    student_id = int(student_id)
    if request.method == "GET":
        return json_response(get_admin_student_detail(student_id))
    elif request.method == "DELETE":
        return json_response(delete_student_account(student_id))
    return json_response({"success": False, "message": "Method not allowed"}, status=405)

@csrf_exempt
@admin_required
def api_admin_student_block(request, student_id):
    return json_response(block_student(int(student_id)))

@csrf_exempt
@admin_required
def api_admin_student_unblock(request, student_id):
    return json_response(unblock_student(int(student_id)))

@csrf_exempt
@admin_required
def api_admin_companies(request):
    args = parse_request_data(request)
    return json_response(get_companies(args))

@csrf_exempt
@admin_required
def api_admin_company_detail(request, client_id):
    client_id = int(client_id)
    if request.method == "GET":
        return json_response(get_company_detail(client_id))
    elif request.method == "DELETE":
        return json_response(delete_company_account(client_id))
    return json_response({"success": False, "message": "Method not allowed"}, status=405)

@csrf_exempt
@admin_required
def api_admin_company_approve(request, client_id):
    return json_response(approve_company(int(client_id)))

@csrf_exempt
@admin_required
def api_admin_company_reject(request, client_id):
    return json_response(reject_company(int(client_id)))

@csrf_exempt
@admin_required
def api_admin_company_block(request, client_id):
    return json_response(block_company(int(client_id)))

@csrf_exempt
@admin_required
def api_admin_jobs(request):
    args = parse_request_data(request)
    return json_response(get_admin_jobs(args))

@csrf_exempt
@admin_required
def api_admin_jobs_stats(request):
    return json_response(get_admin_job_stats())

@csrf_exempt
@admin_required
def api_admin_job_detail(request, job_id):
    return json_response(get_admin_job_detail(int(job_id)))

@csrf_exempt
@admin_required
def api_admin_job_approve(request, job_id):
    return json_response(admin_approve_job(int(job_id)))

@csrf_exempt
@admin_required
def api_admin_job_reject(request, job_id):
    data = parse_request_data(request)
    return json_response(admin_reject_job(int(job_id), rejection_reason=data.get("rejection_reason")))

@csrf_exempt
@admin_required
def api_admin_job_close(request, job_id):
    return json_response(admin_close_job(int(job_id)))

@csrf_exempt
@admin_required
def api_admin_applications(request):
    args = parse_request_data(request)
    return json_response(get_admin_applications(args))

@csrf_exempt
@admin_required
def api_admin_applications_stats(request):
    return json_response(get_admin_app_stats())

@csrf_exempt
@admin_required
def api_admin_application_detail(request, application_id):
    return json_response(get_admin_app_detail(int(application_id)))

@csrf_exempt
@admin_required
def api_admin_application_shortlist(request, application_id):
    data = parse_request_data(request)
    return json_response(admin_shortlist_app(int(application_id), data.get("admin_notes")))

@csrf_exempt
@admin_required
def api_admin_application_reject(request, application_id):
    data = parse_request_data(request)
    return json_response(admin_reject_app(int(application_id), data.get("admin_notes")))

@csrf_exempt
@admin_required
def api_admin_reports_monthly(request):
    months_back = int(request.GET.get("months", 6))
    return json_response(get_monthly_applications(months_back))

@csrf_exempt
@admin_required
def api_admin_reports_breakdown(request):
    return json_response(get_status_breakdown())

@csrf_exempt
@admin_required
def api_admin_notifications(request):
    args = parse_request_data(request)
    return json_response(get_admin_notifications(request.admin_id, args))

@csrf_exempt
@admin_required
def api_admin_notifications_mark_all_read(request):
    return json_response(mark_all_admin_notifications_read(request.admin_id))

@csrf_exempt
@admin_required
def api_admin_notification_mark_read(request, notification_id):
    return json_response(mark_admin_notification_read(int(notification_id)))


# ==========================================
# PUBLIC JOBS & CONTACT VIEWS
# ==========================================

@csrf_exempt
def api_public_jobs(request):
    args = parse_request_data(request)
    return json_response(browse_public_jobs(args))

@csrf_exempt
def api_public_job_detail(request, job_id):
    return json_response(get_public_job_detail(int(job_id)))

@csrf_exempt
def api_contact(request):
    data = parse_request_data(request)
    return json_response(submit_contact_form(data))
