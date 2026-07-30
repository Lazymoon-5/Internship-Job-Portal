from django.urls import path
from api import views

urlpatterns = [
    # Student Auth & Password
    path("student/register", views.api_student_register),
    path("student/login", views.api_student_login),
    path("student/verify-otp", views.api_student_verify_otp),
    path("student/resend-otp", views.api_student_resend_otp),
    path("student/google-login", views.api_student_google_login),
    path("student/forgot-password", views.api_student_forgot_password),
    path("student/reset-password", views.api_student_reset_password),
    path("student/change-password", views.api_student_change_password),

    # Student Profile
    path("student/profile", views.api_student_profile),
    path("student/profile/photo", views.api_student_profile_photo),
    path("student/profile/certifications", views.api_student_certifications),
    path("student/profile/certifications/<int:certification_id>", views.api_student_delete_certification),
    path("student/profile/skills", views.api_student_skills),
    path("student/profile/skills/<int:skill_id>", views.api_student_delete_skill),

    # Student Resumes
    path("student/resume", views.api_student_resumes),
    path("student/resume/<int:resume_id>/set-primary", views.api_student_set_primary_resume),
    path("student/resume/<int:resume_id>", views.api_student_delete_resume),

    # Student Jobs & Applications
    path("student/jobs", views.api_student_jobs),
    path("student/jobs/<int:job_id>", views.api_student_job_detail),
    path("student/jobs/<int:job_id>/apply", views.api_student_apply_job),
    path("student/applications", views.api_student_applications),
    path("student/applications/stats", views.api_student_applications_stats),
    path("student/applications/<int:application_id>", views.api_student_application_detail),

    # Student Notifications
    path("student/notifications", views.api_student_notifications),
    path("student/notifications/mark-all-read", views.api_student_notifications_mark_all_read),
    path("student/notifications/<int:notification_id>/mark-read", views.api_student_notification_mark_read),

    # Client (Company) Auth & Profile
    path("client/register", views.api_client_register),
    path("client/login", views.api_client_login),
    path("client/verify-otp", views.api_client_verify_otp),
    path("client/resend-otp", views.api_client_resend_otp),
    path("client/forgot-password", views.api_client_forgot_password),
    path("client/reset-password", views.api_client_reset_password),
    path("client/change-password", views.api_client_change_password),
    path("client/dashboard/stats", views.api_client_dashboard_stats),
    path("client/profile", views.api_client_profile),

    # Client Jobs & Applicants
    path("client/jobs", views.api_client_jobs),
    path("client/jobs/stats", views.api_client_jobs_stats),
    path("client/jobs/<int:job_id>", views.api_client_job_detail),
    path("client/jobs/<int:job_id>/submit", views.api_client_job_submit),
    path("client/jobs/<int:job_id>/close", views.api_client_job_close),
    path("client/jobs/<int:job_id>/mark-filled", views.api_client_job_mark_filled),
    path("client/jobs/<int:job_id>/applicants", views.api_client_job_applicants),
    path("client/jobs/<int:job_id>/applicants/stats", views.api_client_job_applicants_stats),
    path("client/jobs/<int:job_id>/message-applicants", views.api_client_job_message_applicants),
    path("client/applicants/<int:application_id>", views.api_client_applicant_detail),
    path("client/applicants/<int:application_id>/shortlist", views.api_client_applicant_shortlist),
    path("client/applicants/<int:application_id>/reject", views.api_client_applicant_reject),
    path("client/applicants/<int:application_id>/schedule-interview", views.api_client_applicant_schedule_interview),
    path("client/applicants/<int:application_id>/extend-offer", views.api_client_applicant_extend_offer),

    # Client Notifications
    path("client/notifications", views.api_client_notifications),
    path("client/notifications/mark-all-read", views.api_client_notifications_mark_all_read),
    path("client/notifications/<int:notification_id>/mark-read", views.api_client_notification_mark_read),

    # Admin Auth & Dashboard
    path("admin/login", views.api_admin_login),
    path("admin/change-password", views.api_admin_change_password),
    path("admin/dashboard/stats", views.api_admin_dashboard_stats),

    # Admin Students Management
    path("admin/students", views.api_admin_students),
    path("admin/students/<int:student_id>", views.api_admin_student_detail),
    path("admin/students/<int:student_id>/block", views.api_admin_student_block),
    path("admin/students/<int:student_id>/unblock", views.api_admin_student_unblock),

    # Admin Companies Management
    path("admin/companies", views.api_admin_companies),
    path("admin/companies/<int:client_id>", views.api_admin_company_detail),
    path("admin/companies/<int:client_id>/approve", views.api_admin_company_approve),
    path("admin/companies/<int:client_id>/reject", views.api_admin_company_reject),
    path("admin/companies/<int:client_id>/block", views.api_admin_company_block),

    # Admin Jobs Management
    path("admin/jobs", views.api_admin_jobs),
    path("admin/jobs/stats", views.api_admin_jobs_stats),
    path("admin/jobs/<int:job_id>", views.api_admin_job_detail),
    path("admin/jobs/<int:job_id>/approve", views.api_admin_job_approve),
    path("admin/jobs/<int:job_id>/reject", views.api_admin_job_reject),
    path("admin/jobs/<int:job_id>/close", views.api_admin_job_close),

    # Admin Applications Management
    path("admin/applications", views.api_admin_applications),
    path("admin/applications/stats", views.api_admin_applications_stats),
    path("admin/applications/<int:application_id>", views.api_admin_application_detail),
    path("admin/applications/<int:application_id>/shortlist", views.api_admin_application_shortlist),
    path("admin/applications/<int:application_id>/reject", views.api_admin_application_reject),

    # Admin Reports & Notifications
    path("admin/reports/monthly-applications", views.api_admin_reports_monthly),
    path("admin/reports/status-breakdown", views.api_admin_reports_breakdown),
    path("admin/notifications", views.api_admin_notifications),
    path("admin/notifications/mark-all-read", views.api_admin_notifications_mark_all_read),
    path("admin/notifications/<int:notification_id>/mark-read", views.api_admin_notification_mark_read),

    # Public Jobs & Contact
    path("jobs", views.api_public_jobs),
    path("jobs/<int:job_id>", views.api_public_job_detail),
    path("contact", views.api_contact),
]
