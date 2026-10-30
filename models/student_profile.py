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

from config.database import get_db_connection, _sanitize_db_param

PROFILE_FIELDS = [
    "department", "current_year", "mobile_no", "profile_summary",
    "city", "pincode", "state", "linkedin_url", "enrollment_no",
    "college_address", "course", "gpa_cgpa",
    "experience_level", "years_of_experience", "job_designation",
    "experience_company", "experience_duration",
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
                      profile_completed, experience_level, years_of_experience,
                      job_designation, experience_company, experience_duration
               FROM students WHERE id = %s""",
            (student_id,)
        )
        row = cursor.fetchone()
        cursor.close()
    finally:
        conn.close()

    if row:
        row["gpa"] = row.get("gpa_cgpa")  # legacy alias, per v3 doc §1.3
        row["profile_completion"] = _calculate_completion(row)
        can_apply, missing_sections, missing_fields = get_apply_eligibility(student_id)
        row["can_apply"] = can_apply
        row["missing_sections"] = missing_sections
        row["missing_fields"] = missing_fields
    return row


def _calculate_completion(profile: dict) -> int:
    """0-100 — percentage of profile fields that are actually filled in."""
    checklist = [
        "department", "current_year", "mobile_no", "profile_summary",
        "city", "pincode", "state", "linkedin_url", "enrollment_no",
        "college_address", "course", "gpa_cgpa", "profile_photo_url",
    ]
    filled = sum(1 for field in checklist if profile.get(field))
    return round((filled / len(checklist)) * 100)


def check_apply_eligibility(profile: dict) -> tuple:
    """
    Decides apply eligibility based only on the 3 required sections:
    1. Personal & Academic Details (name, email, mobile_no, department, current_year, city, state, course, enrollment_no, gpa_cgpa, college)
    2. Work Experience (Fresher OR Experienced with at least 1 experience entry)
    3. Skills & Certificates (at least 1 skill)
    Profile photo and certifications are OPTIONAL.
    Returns plain 3-tuple: (can_apply: bool, missing_sections: list[str], missing_fields: list[str])
    """
    if not profile:
        return (
            False,
            ["Personal & Academic Details", "Work Experience", "Skills & Certificates"],
            ["Full Name", "Email", "Phone", "Department", "Current Year", "City", "State", "Course", "Enrollment No", "College", "GPA/CGPA"]
        )

    # Section 1: Personal & Academic Details
    s1_fields = [
        ("name", "Full Name"),
        ("email", "Email"),
        ("mobile_no", "Phone"),
        ("department", "Department"),
        ("current_year", "Current Year"),
        ("city", "City"),
        ("state", "State"),
        ("course", "Course"),
        ("enrollment_no", "Enrollment No"),
        ("college", "College"),
    ]

    missing_fields = []
    for field_key, label in s1_fields:
        val = profile.get(field_key)
        if val is None or not str(val).strip():
            missing_fields.append(label)

    # GPA check (gpa_cgpa or legacy gpa / cgpa)
    gpa_val = profile.get("gpa_cgpa") if profile.get("gpa_cgpa") is not None else profile.get("gpa")
    if gpa_val is None or not str(gpa_val).strip():
        missing_fields.append("GPA/CGPA")

    missing_sections = []
    if missing_fields:
        missing_sections.append("Personal & Academic Details")

    # Section 2: Work Experience
    # Complete when:
    # - experience_level == "Fresher", OR
    # - experience_level == "Experienced" AND at least one work experience entry exists.
    # If experience_level is empty/null, section is incomplete.
    exp_level = (profile.get("experience_level") or "").strip()
    if not exp_level or exp_level not in ("Fresher", "Experienced"):
        missing_sections.append("Work Experience")
    elif exp_level == "Experienced":
        experiences = profile.get("experiences") or []
        has_exp = bool(len(experiences) > 0)
        if not has_exp:
            # Fallback to legacy flat columns on students table if any
            has_exp = bool((profile.get("job_designation") or "").strip() or (profile.get("experience_company") or "").strip())
        if not has_exp:
            missing_sections.append("Work Experience")

    # Section 3: Skills & Certificates (skills required: >= 1, certifications optional)
    skills = profile.get("skills") or []
    has_skills = bool(len(skills) > 0)
    if not has_skills:
        missing_sections.append("Skills & Certificates")

    can_apply = len(missing_sections) == 0
    return (can_apply, missing_sections, missing_fields)


def get_apply_eligibility(student_id: int) -> tuple:
    """
    Single source of truth for student apply eligibility.
    Always loads the student profile, skills, and experiences from the database
    before computing eligibility with check_apply_eligibility.
    Returns plain 3-tuple: (can_apply: bool, missing_sections: list[str], missing_fields: list[str])
    """
    if not student_id:
        return (
            False,
            ["Personal & Academic Details", "Work Experience", "Skills & Certificates"],
            ["Full Name", "Email", "Phone", "Department", "Current Year", "City", "State", "Course", "Enrollment No", "College", "GPA/CGPA"]
        )

    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT id, name, email, college, branch, is_verified, status,
                      department, current_year, mobile_no, profile_summary,
                      city, pincode, state, linkedin_url, enrollment_no,
                      college_address, course, gpa_cgpa, profile_photo_url,
                      profile_completed, experience_level, years_of_experience,
                      job_designation, experience_company, experience_duration
               FROM students WHERE id = %s""",
            (student_id,)
        )
        row = cursor.fetchone()
        cursor.close()
    finally:
        conn.close()

    if not row:
        return (
            False,
            ["Personal & Academic Details", "Work Experience", "Skills & Certificates"],
            ["Full Name", "Email", "Phone", "Department", "Current Year", "City", "State", "Course", "Enrollment No", "College", "GPA/CGPA"]
        )

    row["gpa"] = row.get("gpa_cgpa")

    # Always attach skills and experiences from database
    from models.skill import list_skills
    from models.experience import list_experiences
    try:
        row["skills"] = list_skills(student_id)
    except Exception:
        row["skills"] = []
    try:
        row["experiences"] = list_experiences(student_id)
    except Exception:
        row["experiences"] = []

    return check_apply_eligibility(row)


def update_profile(student_id: int, data: dict) -> bool:
    """
    Updates only the fields present in `data` — supports both the
    3-step "Complete Your Profile" wizard (partial updates per step)
    and the Settings page (full edit). `name` is also editable here
    even though it lives in the core students table (email, however,
    is intentionally NEVER updatable — matches "Cannot Change" in the UI).

    Accepts "gpa" as a legacy alias for "gpa_cgpa" — if the frontend
    sends either key, it saves to the same gpa_cgpa column.
    """
    data = dict(data)  # avoid mutating the caller's dict
    if "gpa" in data and "gpa_cgpa" not in data:
        data["gpa_cgpa"] = data.pop("gpa")

    updatable_fields = ["name"] + PROFILE_FIELDS
    set_clauses = []
    values = []

    for field in updatable_fields:
        if field in data:
            set_clauses.append(f"{field} = %s")
            values.append(_sanitize_db_param(data[field]))

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
