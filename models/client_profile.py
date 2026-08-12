"""
Client (Company) profile — handles the extended profile fields added
to the clients table for the Company Dashboard. Mirrors
models/student_profile.py in pattern.
"""

from config.database import get_db_connection, _sanitize_db_param

PROFILE_FIELDS = [
    "contact", "company_size", "year_established", "city", "pincode", "state",
    "address", "about_company", "company_summary", "hr_name", "hr_contact_email",
    "hr_phone_number", "facebook_url", "linkedin_url", "hiring_locations",
    "preferred_job_types", "company_registration_number", "cin_number",
    "gst_number", "pan_number", "terms_accepted",
]


def get_profile(client_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT id, company_name, email, industry, website, is_verified, admin_status,
                      contact, company_size, year_established, city, pincode, state,
                      address, about_company, company_summary, hr_name, hr_contact_email,
                      hr_phone_number, facebook_url, linkedin_url, hiring_locations,
                      preferred_job_types, company_registration_number, cin_number,
                      gst_number, pan_number, terms_accepted, profile_completed
               FROM clients WHERE id = %s""",
            (client_id,)
        )
        row = cursor.fetchone()
        if row:
            row["profile_completion"] = _calculate_completion(row)
        cursor.close()
        return row
    finally:
        conn.close()


def _calculate_completion(profile: dict) -> int:
    """0-100 — percentage of profile fields that are actually filled in."""
    checklist = [
        "contact", "company_size", "year_established", "city", "pincode", "state",
        "address", "about_company", "company_summary", "hr_name", "hr_contact_email",
        "hr_phone_number", "hiring_locations", "preferred_job_types",
        "company_registration_number",
    ]
    filled = sum(1 for field in checklist if profile.get(field))
    return round((filled / len(checklist)) * 100)


def _sanitize_db_param(val):
    if val is None:
        return None
    if isinstance(val, (list, tuple, set)):
        return ", ".join(str(item) for item in val)
    if isinstance(val, dict):
        import json
        return json.dumps(val)
    return val


def update_profile(client_id: int, data: dict) -> bool:
    """company_name is also editable (matches Basic Details section);
    email is intentionally never updatable."""
    updatable_fields = ["company_name", "industry", "website"] + PROFILE_FIELDS
    set_clauses = []
    values = []

    for field in updatable_fields:
        if field in data:
            set_clauses.append(f"{field} = %s")
            values.append(_sanitize_db_param(data[field]))

    if not set_clauses:
        return False

    values.append(client_id)

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE clients SET {', '.join(set_clauses)} WHERE id = %s",
            values
        )
        conn.commit()
        updated = cursor.rowcount > 0
        cursor.close()
        return updated
    finally:
        conn.close()


def mark_profile_completed(client_id: int) -> bool:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE clients SET profile_completed = TRUE WHERE id = %s", (client_id,))
        conn.commit()
        updated = cursor.rowcount > 0
        cursor.close()
        return updated
    finally:
        conn.close()
