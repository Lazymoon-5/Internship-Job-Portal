"""
Application model. Real MySQL only (same reasoning as job.py — this
is inherently relational, tied to both a student and a job).

create_application() exists here so this file is ready for the future
Student "Apply for Job" API — not part of this delivery, but the model
layer is already built for it.
"""

from config.database import get_db_connection


def create_application(app_data: dict):
    """app_data = {student_id, job_id, cover_letter, portfolio_link}"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO applications (student_id, job_id, cover_letter, portfolio_link)
               VALUES (%s, %s, %s, %s)""",
            (app_data["student_id"], app_data["job_id"],
             app_data.get("cover_letter", ""), app_data.get("portfolio_link", ""))
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        return new_id
    finally:
        conn.close()


def list_applications(search="", status_filter="", page=1, per_page=10):
    """Returns (list_of_application_dicts_with_student_and_job_info, total_count)"""
    offset = (page - 1) * per_page
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        where_clauses = []
        params = []

        if search:
            where_clauses.append("(s.name LIKE %s OR c.company_name LIKE %s OR j.title LIKE %s)")
            like = f"%{search}%"
            params.extend([like, like, like])

        if status_filter:
            where_clauses.append("a.status = %s")
            params.append(status_filter)

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        cursor.execute(
            f"""SELECT COUNT(*) as cnt FROM applications a
                JOIN students s ON a.student_id = s.id
                JOIN jobs j ON a.job_id = j.id
                JOIN clients c ON j.client_id = c.id
                {where_sql}""",
            params
        )
        total = cursor.fetchone()["cnt"]

        cursor.execute(
            f"""SELECT a.id, a.status, a.applied_at, a.updated_at,
                       s.id as student_id, s.name as student_name, s.branch as student_branch,
                       j.id as job_id, j.title as job_title,
                       c.company_name
                FROM applications a
                JOIN students s ON a.student_id = s.id
                JOIN jobs j ON a.job_id = j.id
                JOIN clients c ON j.client_id = c.id
                {where_sql}
                ORDER BY a.applied_at DESC LIMIT %s OFFSET %s""",
            params + [per_page, offset]
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows, total
    finally:
        conn.close()


def get_application_by_id(application_id: int):
    """Full applicant dossier for the Application Detail page."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT a.*,
                      s.name as student_name, s.email as student_email,
                      s.college as student_college, s.branch as student_branch,
                      j.title as job_title, j.job_type,
                      c.company_name
               FROM applications a
               JOIN students s ON a.student_id = s.id
               JOIN jobs j ON a.job_id = j.id
               JOIN clients c ON j.client_id = c.id
               WHERE a.id = %s""",
            (application_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        return row
    finally:
        conn.close()


def update_application_status(application_id: int, status: str, admin_notes: str = None) -> bool:
    """status: 'Applied', 'In Review', 'Shortlisted', 'Interview', 'Offered', or 'Rejected'"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if admin_notes is not None:
            cursor.execute(
                "UPDATE applications SET status = %s, admin_notes = %s WHERE id = %s",
                (status, admin_notes, application_id)
            )
        else:
            cursor.execute(
                "UPDATE applications SET status = %s WHERE id = %s",
                (status, application_id)
            )
        conn.commit()
        updated = cursor.rowcount > 0
        cursor.close()
        return updated
    finally:
        conn.close()


def count_applications() -> int:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM applications")
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    finally:
        conn.close()


def count_applications_by_status(status: str) -> int:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM applications WHERE status = %s", (status,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    finally:
        conn.close()


def monthly_application_counts(months_back: int = 6):
    """Returns list of {month, count} for the Reports & Analytics chart."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT DATE_FORMAT(applied_at, '%Y-%m') as month, COUNT(*) as count
               FROM applications
               WHERE applied_at >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)
               GROUP BY month ORDER BY month ASC""",
            (months_back,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()
