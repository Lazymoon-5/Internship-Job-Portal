"""
Job model. Real MySQL only for now (no in-memory fallback) — jobs are
inherently relational (tied to a client via foreign key), which makes
an in-memory equivalent messy and not worth the complexity here. If
DB isn't available, these functions will raise — that's acceptable
since job management is an Admin-only feature layered on top of an
already-required database.

create_job() exists here so this file is ready for the future Company
"Post a Job" API — not part of this delivery, but the model layer is
already built for it.
"""

from config.database import get_db_connection, _sanitize_db_param
import datetime


def _format_job_date(job: dict) -> dict:
    """
    Converts last_date_to_apply from a datetime.date/datetime object to
    a plain 'YYYY-MM-DD' string, per v3 doc §3 — applied consistently
    everywhere a job dict is returned, since several queries use `j.*`
    wildcards that can't be reformatted at the SQL level individually.
    """
    if job and job.get("last_date_to_apply") is not None:
        value = job["last_date_to_apply"]
        if isinstance(value, (datetime.date, datetime.datetime)):
            job["last_date_to_apply"] = value.strftime("%Y-%m-%d")
    return job


def _format_job_dates(jobs: list) -> list:
    for job in jobs:
        _format_job_date(job)
    return jobs


def _sanitize_db_param(val):
    if val is None:
        return None
    if isinstance(val, (list, tuple, set)):
        return ", ".join(str(item) for item in val)
    if isinstance(val, dict):
        import json
        return json.dumps(val)
    return val


def create_job(job_data: dict):
    """
    job_data = {client_id, title, description, job_type, required_skills,
                eligibility_criteria, location, salary_stipend, last_date_to_apply}
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO jobs (client_id, title, description, job_type, department,
               required_skills, eligibility_criteria, location, salary_stipend, last_date_to_apply)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (_sanitize_db_param(job_data["client_id"]),
             _sanitize_db_param(job_data.get("title", "")),
             _sanitize_db_param(job_data.get("description", "")),
             _sanitize_db_param(job_data.get("job_type", "Internship")),
             _sanitize_db_param(job_data.get("department", "")),
             _sanitize_db_param(job_data.get("required_skills", "")),
             _sanitize_db_param(job_data.get("eligibility_criteria", "")),
             _sanitize_db_param(job_data.get("location", "")),
             _sanitize_db_param(job_data.get("salary_stipend", "")),
             job_data.get("last_date_to_apply"))
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        return new_id
    finally:
        conn.close()


def list_jobs(search="", status_filter="", page=1, per_page=10):
    """Returns (list_of_job_dicts_with_company_name_and_application_count, total_count)"""
    offset = (page - 1) * per_page
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        where_clauses = []
        params = []

        if search:
            where_clauses.append("(j.title LIKE %s OR c.company_name LIKE %s)")
            like = f"%{search}%"
            params.extend([like, like])

        if status_filter:
            where_clauses.append("j.status = %s")
            params.append(status_filter)

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        cursor.execute(
            f"""SELECT COUNT(*) as cnt FROM jobs j
                JOIN clients c ON j.client_id = c.id {where_sql}""",
            params
        )
        total = cursor.fetchone()["cnt"]

        cursor.execute(
            f"""SELECT j.*, c.company_name,
                       (SELECT COUNT(*) FROM applications a WHERE a.job_id = j.id) as applications_count
                FROM jobs j
                JOIN clients c ON j.client_id = c.id
                {where_sql}
                ORDER BY j.created_at DESC LIMIT %s OFFSET %s""",
            params + [per_page, offset]
        )
        rows = cursor.fetchall()
        cursor.close()
        return _format_job_dates(rows), total
    finally:
        conn.close()


def get_job_by_id(job_id: int):
    """Returns full job detail including company info, for the Job Post Detail page."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT j.*, c.company_name, c.email as company_email,
                      c.website as company_website, c.industry as company_industry,
                      (SELECT COUNT(*) FROM applications a WHERE a.job_id = j.id) as total_applications,
                      (SELECT COUNT(*) FROM applications a WHERE a.job_id = j.id AND a.status = 'Shortlisted') as shortlisted_count,
                      (SELECT COUNT(*) FROM applications a WHERE a.job_id = j.id AND a.status = 'Rejected') as rejected_count,
                      (SELECT COUNT(*) FROM applications a WHERE a.job_id = j.id AND a.status IN ('Applied','In Review')) as pending_count
               FROM jobs j
               JOIN clients c ON j.client_id = c.id
               WHERE j.id = %s""",
            (job_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        return _format_job_date(row)
    finally:
        conn.close()


def update_job_status(job_id: int, status: str, rejection_reason: str = None) -> bool:
    """status: 'Pending', 'Approved', 'Rejected', or 'Closed'.
    rejection_reason is optional, only meaningful when status='Rejected'."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if rejection_reason is not None:
            cursor.execute(
                "UPDATE jobs SET status = %s, rejection_reason = %s WHERE id = %s",
                (status, rejection_reason, job_id)
            )
        else:
            cursor.execute("UPDATE jobs SET status = %s WHERE id = %s", (status, job_id))
        conn.commit()
        updated = cursor.rowcount > 0
        cursor.close()
        return updated
    finally:
        conn.close()


def count_jobs() -> int:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM jobs")
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    finally:
        conn.close()


def count_jobs_by_status(status: str) -> int:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE status = %s", (status,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    finally:
        conn.close()


# ================= Student-facing (browse/detail) =================
# Only shows jobs with status='Approved' — students should never see
# Pending/Rejected/Closed postings.

def list_approved_jobs(search="", job_type="", location="", page=1, per_page=10):
    """Returns (list_of_job_dicts, total_count) — for the Browse Jobs page."""
    offset = (page - 1) * per_page
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        where_clauses = ["j.status = 'Approved'"]
        params = []

        if search:
            where_clauses.append("(j.title LIKE %s OR c.company_name LIKE %s)")
            like = f"%{search}%"
            params.extend([like, like])

        if job_type:
            where_clauses.append("j.job_type = %s")
            params.append(job_type)

        if location:
            where_clauses.append("j.location LIKE %s")
            params.append(f"%{location}%")

        where_sql = "WHERE " + " AND ".join(where_clauses)

        cursor.execute(
            f"SELECT COUNT(*) as cnt FROM jobs j JOIN clients c ON j.client_id = c.id {where_sql}",
            params
        )
        total = cursor.fetchone()["cnt"]

        cursor.execute(
            f"""SELECT j.id, j.title, j.job_type, j.department, j.location, j.salary_stipend,
                       j.last_date_to_apply, j.created_at, c.company_name
                FROM jobs j
                JOIN clients c ON j.client_id = c.id
                {where_sql}
                ORDER BY j.created_at DESC LIMIT %s OFFSET %s""",
            params + [per_page, offset]
        )
        rows = cursor.fetchall()
        cursor.close()
        return _format_job_dates(rows), total
    finally:
        conn.close()


def get_approved_job_by_id(job_id: int):
    """Returns None if the job doesn't exist OR isn't Approved — students
    should get a 404 either way, not be able to tell the difference."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT j.*, c.company_name, c.industry as company_industry,
                      c.website as company_website
               FROM jobs j
               JOIN clients c ON j.client_id = c.id
               WHERE j.id = %s AND j.status = 'Approved'""",
            (job_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        return _format_job_date(row)
    finally:
        conn.close()


# ================= Client-facing (Post a Job, Jobs Posted, Dashboard) =================

def list_jobs_by_client(client_id: int, search="", status_filter="", page=1, per_page=10):
    """Returns (list_of_job_dicts, total_count) — for the Jobs Posted page."""
    offset = (page - 1) * per_page
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        where_clauses = ["j.client_id = %s"]
        params = [client_id]

        if search:
            where_clauses.append("j.title LIKE %s")
            params.append(f"%{search}%")

        if status_filter:
            where_clauses.append("j.status = %s")
            params.append(status_filter)

        where_sql = "WHERE " + " AND ".join(where_clauses)

        cursor.execute(f"SELECT COUNT(*) as cnt FROM jobs j {where_sql}", params)
        total = cursor.fetchone()["cnt"]

        cursor.execute(
            f"""SELECT j.*,
                       (SELECT COUNT(*) FROM applications a WHERE a.job_id = j.id) as applications_count
                FROM jobs j
                {where_sql}
                ORDER BY j.created_at DESC LIMIT %s OFFSET %s""",
            params + [per_page, offset]
        )
        rows = cursor.fetchall()
        cursor.close()
        return _format_job_dates(rows), total
    finally:
        conn.close()


def get_job_owned_by_client(job_id: int, client_id: int):
    """Returns the job only if it belongs to this client — else None.
    Used to enforce that a company can only edit/close/view its OWN jobs."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM jobs WHERE id = %s AND client_id = %s",
            (job_id, client_id)
        )
        row = cursor.fetchone()
        cursor.close()
        return _format_job_date(row)
    finally:
        conn.close()


def update_job(job_id: int, client_id: int, data: dict) -> bool:
    """Only updates if the job belongs to this client."""
    updatable_fields = [
        "title", "description", "job_type", "department", "required_skills",
        "eligibility_criteria", "location", "salary_stipend", "last_date_to_apply"
    ]
    set_clauses = []
    values = []

    for field in updatable_fields:
        if field in data:
            set_clauses.append(f"{field} = %s")
            values.append(_sanitize_db_param(data[field]))

    if not set_clauses:
        return False

    values.extend([job_id, client_id])

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE jobs SET {', '.join(set_clauses)} WHERE id = %s AND client_id = %s",
            values
        )
        conn.commit()
        updated = cursor.rowcount > 0
        cursor.close()
        return updated
    finally:
        conn.close()


def update_job_status_by_client(job_id: int, client_id: int, status: str) -> bool:
    """status: 'Draft', 'Pending', 'Closed', or 'Filled' — Approved/Rejected
    are Admin-only transitions (see update_job_status in the admin section above)."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE jobs SET status = %s WHERE id = %s AND client_id = %s",
            (status, job_id, client_id)
        )
        conn.commit()
        updated = cursor.rowcount > 0
        cursor.close()
        return updated
    finally:
        conn.close()


def get_client_job_stats(client_id: int):
    """For the Jobs Posted page's 4 stat cards."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM jobs WHERE client_id = %s", (client_id,))
        total = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM jobs WHERE client_id = %s AND status = 'Approved'",
            (client_id,)
        )
        active = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM jobs WHERE client_id = %s AND status = 'Filled'",
            (client_id,)
        )
        filled = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM jobs WHERE client_id = %s AND status IN ('Closed','Draft')",
            (client_id,)
        )
        closed_or_draft = cursor.fetchone()[0]

        cursor.close()
        return {
            "total_listings": total,
            "active_now": active,
            "positions_filled": filled,
            "closed_or_drafts": closed_or_draft,
        }
    finally:
        conn.close()


def get_client_dashboard_stats(client_id: int):
    """For the Company Dashboard's 4 stat cards."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM jobs WHERE client_id = %s AND status = 'Approved'",
            (client_id,)
        )
        active_posts = cursor.fetchone()[0]

        cursor.execute(
            """SELECT COUNT(*) FROM applications a
               JOIN jobs j ON a.job_id = j.id
               WHERE j.client_id = %s""",
            (client_id,)
        )
        total_applicants = cursor.fetchone()[0]

        cursor.execute(
            """SELECT COUNT(*) FROM applications a
               JOIN jobs j ON a.job_id = j.id
               WHERE j.client_id = %s AND a.status = 'Shortlisted'""",
            (client_id,)
        )
        shortlisted = cursor.fetchone()[0]

        cursor.execute(
            """SELECT COUNT(*) FROM applications a
               JOIN jobs j ON a.job_id = j.id
               WHERE j.client_id = %s AND a.status = 'Offered'""",
            (client_id,)
        )
        offers_made = cursor.fetchone()[0]

        cursor.close()
        return {
            "active_job_posts": active_posts,
            "total_applicants": total_applicants,
            "shortlisted": shortlisted,
            "offers_made": offers_made,
        }
    finally:
        conn.close()


def get_active_jobs_for_client(client_id: int, limit=5):
    """For the Dashboard's 'Active Jobs' panel."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT j.id, j.title, j.status, j.last_date_to_apply,
                      (SELECT COUNT(*) FROM applications a WHERE a.job_id = j.id) as applications_count
               FROM jobs j
               WHERE j.client_id = %s AND j.status IN ('Approved','Pending')
               ORDER BY j.created_at DESC LIMIT %s""",
            (client_id, limit)
        )
        rows = cursor.fetchall()
        cursor.close()
        return _format_job_dates(rows)
    finally:
        conn.close()
