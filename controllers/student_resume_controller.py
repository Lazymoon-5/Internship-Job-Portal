import re
import models.resume as resume_model

DRIVE_OR_PDF_REGEX = re.compile(r"(drive\.google\.com/file/d/|\.pdf(\?.*)?$)", re.IGNORECASE)


def get_resumes(student_id):
    resumes = resume_model.list_resumes(student_id)
    return {"success": True, "resumes": resumes}, 200


def add_resume(student_id, data):
    filename = (data.get("filename") or "").strip()
    file_url = (data.get("file_url") or "").strip()

    if not filename or not file_url:
        return {"success": False, "message": "filename and file_url are required."}, 400

    if not DRIVE_OR_PDF_REGEX.search(file_url):
        return {
            "success": False,
            "message": "Resume link must be a Google Drive file link or a direct .pdf URL. "
                       "If using Google Drive, make sure the file is shared as "
                       "\"Anyone with the link — Viewer\" so companies can view it."
        }, 400

    resumes = resume_model.list_resumes(student_id)
    if len(resumes) >= 5:
        return {
            "success": False,
            "message": "Maximum of 5 resumes allowed. Delete one before adding another."
        }, 400

    new_id = resume_model.add_resume(student_id, filename, file_url, data.get("is_primary", False))
    return {"success": True, "message": "Resume added.", "id": new_id}, 201


def set_primary_resume(student_id, resume_id):
    updated = resume_model.set_primary_resume(resume_id, student_id)
    if not updated:
        return {"success": False, "message": "Resume not found."}, 404
    return {"success": True, "message": "Primary resume updated."}, 200


def delete_resume(student_id, resume_id):
    deleted = resume_model.delete_resume(resume_id, student_id)
    if not deleted:
        return {"success": False, "message": "Resume not found."}, 404
    return {"success": True, "message": "Resume deleted."}, 200
