"""
Student Profile controller — powers My Profile (view), Settings (edit),
and the 3-step Complete Your Profile wizard. All three UI flows hit the
same underlying GET/PUT profile endpoints — the wizard just calls PUT
multiple times (once per section) and marks completion on the final step.
"""

import models.student_profile as profile_model
import models.certification as certification_model
import models.skill as skill_model


def get_profile(student_id):
    profile = profile_model.get_profile(student_id)
    if not profile:
        return {"success": False, "message": "Student not found."}, 404

    profile["certifications"] = certification_model.list_certifications(student_id)
    profile["skills"] = skill_model.list_skills(student_id)

    return {"success": True, "profile": profile}, 200


def update_profile(student_id, data, mark_completed=False):
    updated = profile_model.update_profile(student_id, data)

    if mark_completed:
        profile_model.mark_profile_completed(student_id)

    if not updated and not mark_completed:
        return {"success": False, "message": "No valid fields provided to update."}, 400

    return {"success": True, "message": "Profile updated successfully."}, 200


def update_profile_photo(student_id, data):
    photo_url = data.get("photo_url")
    if not photo_url:
        return {"success": False, "message": "photo_url is required."}, 400

    profile_model.update_profile_photo(student_id, photo_url)
    return {"success": True, "message": "Profile photo updated."}, 200


def add_certification(student_id, data):
    certificate_name = (data.get("certificate_name") or "").strip()
    if not certificate_name:
        return {"success": False, "message": "certificate_name is required."}, 400

    new_id = certification_model.add_certification(
        student_id, certificate_name,
        data.get("issued_by", ""), data.get("file_url", "")
    )
    return {"success": True, "message": "Certification added.", "id": new_id}, 201


def delete_certification(student_id, certification_id):
    deleted = certification_model.delete_certification(certification_id, student_id)
    if not deleted:
        return {"success": False, "message": "Certification not found."}, 404
    return {"success": True, "message": "Certification removed."}, 200


def add_skill(student_id, data):
    skill_name = (data.get("skill_name") or "").strip()
    if not skill_name:
        return {"success": False, "message": "skill_name is required."}, 400

    new_id = skill_model.add_skill(student_id, skill_name, data.get("level", ""))
    return {"success": True, "message": "Skill added.", "id": new_id}, 201


def delete_skill(student_id, skill_id):
    deleted = skill_model.delete_skill(skill_id, student_id)
    if not deleted:
        return {"success": False, "message": "Skill not found."}, 404
    return {"success": True, "message": "Skill removed."}, 200
