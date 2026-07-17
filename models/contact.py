"""
Contact form submissions — from the public Landing Website's Contact page.
Stored for record-keeping AND emailed to the team immediately.
"""

from config.database import get_db_connection


def create_contact_submission(name: str, email: str, message: str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO contact_submissions (name, email, message) VALUES (%s, %s, %s)",
            (name, email, message)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        return new_id
    finally:
        conn.close()


def mark_notified(submission_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE contact_submissions SET notified = TRUE WHERE id = %s",
            (submission_id,)
        )
        conn.commit()
        cursor.close()
    finally:
        conn.close()
