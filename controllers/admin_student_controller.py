"""
Manage Students controller — list/search/filter, block/unblock, delete.
"""

import models.student as student_model
import models.student_profile as profile_model
import models.skill as skill_model
import models.certification as certification_model
import models.experience as experience_model
import models.resume as resume_model
import models.application as application_model


def get_students(args):
    search = args.get("search", "").strip()
    status_filter = args.get("status", "").strip()
    page = int(args.get("page", 1))
    per_page = int(args.get("per_page", 10))

    students, total = student_model.list_students(search, status_filter, page, per_page)

    return {
        "success": True,
        "students": students,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if per_page else 1,
    }, 200


def get_student_detail(student_id):
    """
    Returns the SAME rich profile shape as the student's own
    GET /api/student/profile — plus their resume and application
    history, since Admin needs the full picture, not just auth fields.
    Fixes a real gap: this previously only returned Student.to_dict()
    (name/email/college/branch/status), missing everything else.
    """
    profile = profile_model.get_profile(student_id)
    if not profile:
        return {"success": False, "message": "Student not found."}, 404

    profile["phone"] = profile.get("mobile_no")  # alias, matches applicant-view naming
    profile["skills"] = skill_model.list_skills(student_id)
    profile["certifications"] = certification_model.list_certifications(student_id)
    profile["certificates"] = profile["certifications"]  # alias, per doc's "either name" note
    profile["experiences"] = experience_model.list_experiences(student_id)

    primary_resume = resume_model.get_primary_resume(student_id)
    profile["resume_url"] = primary_resume["file_url"] if primary_resume else None
    profile["resumes"] = resume_model.list_resumes(student_id)

    applications, _ = application_model.list_applications_by_student(student_id, page=1, per_page=100)
    profile["applications"] = [
        {
            "job_title": a["job_title"],
            "company_name": a["company_name"],
            "status": a["status"],
            "applied_date": a["applied_at"],
        }
        for a in applications
    ]

    return {"success": True, "student": profile}, 200


def block_student(student_id):
    student = student_model.find_by_id(student_id)
    if not student:
        return {"success": False, "message": "Student not found."}, 404

    student_model.update_status(student_id, "Blocked")
    return {"success": True, "message": "Student account blocked."}, 200


def unblock_student(student_id):
    student = student_model.find_by_id(student_id)
    if not student:
        return {"success": False, "message": "Student not found."}, 404

    student_model.update_status(student_id, "Active")
    return {"success": True, "message": "Student account unblocked."}, 200


def delete_student_account(student_id):
    student = student_model.find_by_id(student_id)
    if not student:
        return {"success": False, "message": "Student not found."}, 404

    student_model.delete_student(student_id)
    return {"success": True, "message": "Student account deleted."}, 200
