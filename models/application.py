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


# ================= Student-facing (apply/my applications) =================

def create_application_with_check(student_id: int, job_id: int, cover_letter: str,
                                     portfolio_link: str, resume_id):
    """
    Returns (application_id, error_message). error_message is None on
    success. Checks the job exists+is Approved and the student hasn't
    already applied, before inserting — clean errors instead of relying
    on the DB's UNIQUE constraint to fail loudly.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, status FROM jobs WHERE id = %s", (job_id,))
        job = cursor.fetchone()
        if not job:
            cursor.close()
            return None, "Job not found."
        if job["status"] != "Approved":
            cursor.close()
            return None, "This job is not currently accepting applications."

        cursor.execute(
            "SELECT id FROM applications WHERE student_id = %s AND job_id = %s",
            (student_id, job_id)
        )
        if cursor.fetchone():
            cursor.close()
            return None, "You have already applied to this job."

        cursor2 = conn.cursor()
        cursor2.execute(
            """INSERT INTO applications (student_id, job_id, resume_id, cover_letter, portfolio_link)
               VALUES (%s, %s, %s, %s, %s)""",
            (student_id, job_id, resume_id, cover_letter, portfolio_link)
        )
        conn.commit()
        new_id = cursor2.lastrowid
        cursor2.close()
        cursor.close()
        return new_id, None
    finally:
        conn.close()


def list_applications_by_student(student_id: int, page=1, per_page=20):
    offset = (page - 1) * per_page
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT COUNT(*) as cnt FROM applications WHERE student_id = %s",
            (student_id,)
        )
        total = cursor.fetchone()["cnt"]

        cursor.execute(
            """SELECT a.id, a.status, a.applied_at, a.updated_at,
                      j.id as job_id, j.title as job_title, j.location, j.job_type,
                      c.company_name
               FROM applications a
               JOIN jobs j ON a.job_id = j.id
               JOIN clients c ON j.client_id = c.id
               WHERE a.student_id = %s
               ORDER BY a.applied_at DESC LIMIT %s OFFSET %s""",
            (student_id, per_page, offset)
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows, total
    finally:
        conn.close()


def get_student_application_stats(student_id: int):
    """For the Applied Status page's 4 stat cards."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM applications WHERE student_id = %s", (student_id,))
        total = cursor.fetchone()[0]

        cursor.execute(
            """SELECT COUNT(*) FROM applications
               WHERE student_id = %s AND status IN ('Applied','In Review','Shortlisted','Interview')""",
            (student_id,)
        )
        active = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM applications WHERE student_id = %s AND status = 'Offered'",
            (student_id,)
        )
        offers = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM applications WHERE student_id = %s AND status = 'Rejected'",
            (student_id,)
        )
        rejected = cursor.fetchone()[0]

        cursor.close()
        return {
            "total_applied": total,
            "active_progress": active,
            "offers_received": offers,
            "rejected": rejected,
        }
    finally:
        conn.close()


def get_student_application_detail(application_id: int, student_id: int):
    """student_id required — a student can only view THEIR OWN application detail."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT a.*, j.title as job_title, j.job_type, j.location,
                      c.company_name
               FROM applications a
               JOIN jobs j ON a.job_id = j.id
               JOIN clients c ON j.client_id = c.id
               WHERE a.id = %s AND a.student_id = %s""",
            (application_id, student_id)
        )
        row = cursor.fetchone()
        cursor.close()
        return row
    finally:
        conn.close()


# ================= Client-facing (Manage Applicants) =================

def list_applications_for_job(job_id: int, client_id: int, search="", status_filter="",
                                 page=1, per_page=10):
    """
    Returns (list_of_application_dicts, total_count) — for the Applicant
    Management page. client_id required so a company can only ever see
    applicants for jobs THEY posted, not another company's.
    """
    offset = (page - 1) * per_page
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        # Ownership check first
        cursor.execute("SELECT id FROM jobs WHERE id = %s AND client_id = %s", (job_id, client_id))
        if not cursor.fetchone():
            cursor.close()
            return None, 0  # signals "not your job" to the controller

        where_clauses = ["a.job_id = %s"]
        params = [job_id]

        if search:
            where_clauses.append("s.name LIKE %s")
            params.append(f"%{search}%")

        if status_filter:
            where_clauses.append("a.status = %s")
            params.append(status_filter)

        where_sql = "WHERE " + " AND ".join(where_clauses)

        cursor.execute(
            f"""SELECT COUNT(*) as cnt FROM applications a
                JOIN students s ON a.student_id = s.id
                {where_sql}""",
            params
        )
        total = cursor.fetchone()["cnt"]

        cursor.execute(
            f"""SELECT a.id, a.status, a.applied_at, a.viewed_by_company,
                       s.id as student_id, s.name as student_name, s.college, s.branch,
                       s.current_year, s.gpa_cgpa, s.profile_summary
                FROM applications a
                JOIN students s ON a.student_id = s.id
                {where_sql}
                ORDER BY a.applied_at DESC LIMIT %s OFFSET %s""",
            params + [per_page, offset]
        )
        rows = cursor.fetchall()

        # Attach each applicant's skills (separate query per row, since
        # skills live in their own table — acceptable at this page size,
        # 10-20 rows per page).
        for row in rows:
            cursor2 = conn.cursor(dictionary=True)
            cursor2.execute(
                "SELECT skill_name FROM skills WHERE student_id = %s", (row["student_id"],)
            )
            row["skills"] = [s["skill_name"] for s in cursor2.fetchall()]
            cursor2.close()

        cursor.close()
        return rows, total
    finally:
        conn.close()


def get_job_applicant_stats(job_id: int, client_id: int):
    """For the Applicant Management page's 4 stat cards."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM jobs WHERE id = %s AND client_id = %s", (job_id, client_id))
        if not cursor.fetchone():
            cursor.close()
            return None

        cursor.execute("SELECT COUNT(*) FROM applications WHERE job_id = %s", (job_id,))
        total = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM applications WHERE job_id = %s AND viewed_by_company = FALSE",
            (job_id,)
        )
        new_unseen = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM applications WHERE job_id = %s AND status = 'Shortlisted'",
            (job_id,)
        )
        shortlisted = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM applications WHERE job_id = %s AND status = 'Rejected'",
            (job_id,)
        )
        rejected = cursor.fetchone()[0]

        cursor.close()
        return {
            "total_received": total,
            "new_unseen": new_unseen,
            "shortlisted": shortlisted,
            "rejected": rejected,
        }
    finally:
        conn.close()


def get_applicant_profile_for_client(application_id: int, client_id: int):
    """
    Full Applicant Profile detail for the company to review — including
    student academic info, skills, resume link. client_id required so a
    company can only view applicants to THEIR OWN job postings.
    Also marks the application as viewed (for the New/Unseen count).
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT a.*, j.title as job_title, j.client_id,
                      s.id as student_id, s.name as student_name, s.email as student_email,
                      s.college, s.branch, s.current_year, s.gpa_cgpa, s.profile_summary,
                      s.linkedin_url, s.city, s.state
               FROM applications a
               JOIN jobs j ON a.job_id = j.id
               JOIN students s ON a.student_id = s.id
               WHERE a.id = %s AND j.client_id = %s""",
            (application_id, client_id)
        )
        row = cursor.fetchone()

        if row and not row["viewed_by_company"]:
            cursor2 = conn.cursor()
            cursor2.execute(
                "UPDATE applications SET viewed_by_company = TRUE WHERE id = %s",
                (application_id,)
            )
            conn.commit()
            cursor2.close()
            row["viewed_by_company"] = True  # reflect the update in the returned data too

        if row:
            cursor3 = conn.cursor(dictionary=True)
            cursor3.execute(
                "SELECT skill_name, level FROM skills WHERE student_id = %s", (row["student_id"],)
            )
            row["skills"] = cursor3.fetchall()
            cursor3.close()

        cursor.close()
        return row
    finally:
        conn.close()


def update_application_status_by_client(application_id: int, client_id: int, status: str) -> bool:
    """status: 'Shortlisted' or 'Rejected' — client_id required for ownership check."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE applications a
               JOIN jobs j ON a.job_id = j.id
               SET a.status = %s
               WHERE a.id = %s AND j.client_id = %s""",
            (status, application_id, client_id)
        )
        conn.commit()
        updated = cursor.rowcount > 0
        cursor.close()
        return updated
    finally:
        conn.close()



def get_applicant_emails_for_job(job_id: int, client_id: int):
    """Returns list of {student_name, student_email} for every applicant
    to this job — client_id required for ownership check."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM jobs WHERE id = %s AND client_id = %s", (job_id, client_id))
        if not cursor.fetchone():
            cursor.close()
            return None  # not this client's job

        cursor.execute(
            """SELECT s.name as student_name, s.email as student_email
               FROM applications a
               JOIN students s ON a.student_id = s.id
               WHERE a.job_id = %s""",
            (job_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()
