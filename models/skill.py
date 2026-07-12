from config.database import get_db_connection


def add_skill(student_id: int, skill_name: str, level: str = ""):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO skills (student_id, skill_name, level) VALUES (%s, %s, %s)",
            (student_id, skill_name, level)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        return new_id
    finally:
        conn.close()


def list_skills(student_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM skills WHERE student_id = %s ORDER BY created_at DESC",
            (student_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()


def delete_skill(skill_id: int, student_id: int) -> bool:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM skills WHERE id = %s AND student_id = %s",
            (skill_id, student_id)
        )
        conn.commit()
        deleted = cursor.rowcount > 0
        cursor.close()
        return deleted
    finally:
        conn.close()
