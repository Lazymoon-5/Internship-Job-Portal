from config.database import get_db_connection


def add_resume(student_id: int, filename: str, file_url: str, is_primary: bool = False):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # If this is the student's first resume, make it primary
        # automatically regardless of what was passed in.
        cursor.execute("SELECT COUNT(*) FROM resumes WHERE student_id = %s", (student_id,))
        existing_count = cursor.fetchone()[0]
        if existing_count == 0:
            is_primary = True

        if is_primary:
            # Only one resume can be primary — unset any existing one first.
            cursor.execute("UPDATE resumes SET is_primary = FALSE WHERE student_id = %s", (student_id,))

        cursor.execute(
            "INSERT INTO resumes (student_id, filename, file_url, is_primary) VALUES (%s, %s, %s, %s)",
            (student_id, filename, file_url, is_primary)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        return new_id
    finally:
        conn.close()


def list_resumes(student_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM resumes WHERE student_id = %s ORDER BY is_primary DESC, uploaded_at DESC",
            (student_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()


def get_primary_resume(student_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM resumes WHERE student_id = %s AND is_primary = TRUE LIMIT 1",
            (student_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        return row
    finally:
        conn.close()


def set_primary_resume(resume_id: int, student_id: int) -> bool:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Confirm this resume actually belongs to this student first
        cursor.execute("SELECT id FROM resumes WHERE id = %s AND student_id = %s", (resume_id, student_id))
        if not cursor.fetchone():
            cursor.close()
            return False

        cursor.execute("UPDATE resumes SET is_primary = FALSE WHERE student_id = %s", (student_id,))
        cursor.execute("UPDATE resumes SET is_primary = TRUE WHERE id = %s", (resume_id,))
        conn.commit()
        cursor.close()
        return True
    finally:
        conn.close()


def delete_resume(resume_id: int, student_id: int) -> bool:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT is_primary FROM resumes WHERE id = %s AND student_id = %s",
            (resume_id, student_id)
        )
        row = cursor.fetchone()
        if not row:
            cursor.close()
            return False
        was_primary = row[0]

        cursor.execute("DELETE FROM resumes WHERE id = %s AND student_id = %s", (resume_id, student_id))
        conn.commit()
        deleted = cursor.rowcount > 0

        # If the deleted resume was primary, promote the most recent
        # remaining one to primary automatically, so there's never a
        # gap where a student has resumes but none marked primary.
        if deleted and was_primary:
            cursor.execute(
                "SELECT id FROM resumes WHERE student_id = %s ORDER BY uploaded_at DESC LIMIT 1",
                (student_id,)
            )
            next_row = cursor.fetchone()
            if next_row:
                cursor.execute("UPDATE resumes SET is_primary = TRUE WHERE id = %s", (next_row[0],))
                conn.commit()

        cursor.close()
        return deleted
    finally:
        conn.close()
