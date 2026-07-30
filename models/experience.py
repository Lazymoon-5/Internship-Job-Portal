"""
Student work experiences — one-to-many, per v3 doc §1.2 update.

Kept separate from the flat experience_level/years_of_experience/
job_designation/experience_company/experience_duration columns on
`students` (still supported for backward compatibility — the frontend
sends both the flat "first row" fields AND this array; we store both
independently, no conflict).
"""

from config.database import get_db_connection


def replace_experiences(student_id: int, experiences: list):
    """
    Replaces ALL of a student's work experiences with the given list —
    matches how a profile save naturally works (frontend sends its
    current full list each time, not incremental add/remove). Simpler
    and more predictable than trying to diff/merge.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM student_experiences WHERE student_id = %s", (student_id,))

        for index, exp in enumerate(experiences):
            cursor.execute(
                """INSERT INTO student_experiences
                   (student_id, job_designation, company, duration, years, sort_order)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    student_id,
                    exp.get("job_designation", ""),
                    exp.get("company", ""),
                    exp.get("duration", ""),
                    exp.get("years", 0) or 0,
                    index,
                )
            )
        conn.commit()
        cursor.close()
    finally:
        conn.close()


def list_experiences(student_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT id, job_designation, company, duration, years
               FROM student_experiences
               WHERE student_id = %s
               ORDER BY sort_order ASC""",
            (student_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()
