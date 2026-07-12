from config.database import get_db_connection


def add_certification(student_id: int, certificate_name: str, issued_by: str = "", file_url: str = ""):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO certifications (student_id, certificate_name, issued_by, file_url) VALUES (%s, %s, %s, %s)",
            (student_id, certificate_name, issued_by, file_url)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        return new_id
    finally:
        conn.close()


def list_certifications(student_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM certifications WHERE student_id = %s ORDER BY created_at DESC",
            (student_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()


def delete_certification(certification_id: int, student_id: int) -> bool:
    """student_id is required too, so a student can only delete their OWN certifications."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM certifications WHERE id = %s AND student_id = %s",
            (certification_id, student_id)
        )
        conn.commit()
        deleted = cursor.rowcount > 0
        cursor.close()
        return deleted
    finally:
        conn.close()
