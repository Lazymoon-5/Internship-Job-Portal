"""
Manage Students controller — list/search/filter, block/unblock, delete.
"""

import models.student as student_model


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
    student = student_model.find_by_id(student_id)
    if not student:
        return {"success": False, "message": "Student not found."}, 404
    return {"success": True, "student": student.to_dict()}, 200


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
