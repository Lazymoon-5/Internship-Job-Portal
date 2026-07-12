"""
Student profile — handles the extended profile fields (department,
college address, GPA, LinkedIn, etc.) added to the students table for
the Student Dashboard. Kept separate from models/student.py (which
handles auth: register/login/OTP) to avoid touching every existing
Student(...) construction site across the codebase.

Real MySQL only — no in-memory fallback, since profile management is
a Dashboard feature layered on top of an already-required database
(consistent with jobs/applications/resumes).
"""

from config.database import get_db_connection

PROFILE_FIELDS = [
    "department", "current_year", "mobile_no", "profile_summary",
    "city", "pincode", "state", "linkedin_url", "enrollment_no",
    "college_address", "course", "gpa_cgpa",
]


def get_profile(student_id: int):
    """Returns full profile dict, or None if student doesn't exist."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT id, name, email, college, branch, is_verified, status,
                      department, current_year, mobile_no, profile_summary,
                      city, pincode, state, linkedin_url, enrollment_no,
                      college_address, course, gpa_cgpa, profile_photo_url,
                      profile_completed
               FROM students WHERE id = %s""",
            (student_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        return row
    finally:
        conn.close()


def update_profile(student_id: int, data: dict) -> bool:
    """
    Updates only the fields present in `data` — supports both the
    3-step "Complete Your Profile" wizard (partial updates per step)
    and the Settings page (full edit). `name` is also editable here
    even though it lives in the core students table (email, however,
    is intentionally NEVER updatable — matches "Cannot Change" in the UI).
    """
    updatable_fields = ["name"] + PROFILE_FIELDS
    set_clauses = []
    values = []

    for field in updatable_fields:
        if field in data:
            set_clauses.append(f"{field} = %s")
            values.append(data[field])

    if not set_clauses:
        return False  # nothing to update

    values.append(student_id)

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE students SET {', '.join(set_clauses)} WHERE id = %s",
            values
        )
        conn.commit()
        updated = cursor.rowcount > 0
        cursor.close()
        return updated
    finally:
        conn.close()


def update_profile_photo(student_id: int, photo_url: str) -> bool:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET profile_photo_url = %s WHERE id = %s",
            (photo_url, student_id)
        )
        conn.commit()
        updated = cursor.rowcount > 0
        cursor.close()
        return updated
    finally:
        conn.close()


def mark_profile_completed(student_id: int) -> bool:
    """Called after the 3rd/final step of the profile completion wizard."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET profile_completed = TRUE WHERE id = %s",
            (student_id,)
        )
        conn.commit()
        updated = cursor.rowcount > 0
        cursor.close()
        return updated
    finally:
        conn.close()
