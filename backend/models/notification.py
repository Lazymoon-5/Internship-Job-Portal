"""
Notification model — shared across Student, Client, and Admin.
user_type + user_id together identify who a notification belongs to.
"""

from config.database import get_db_connection, is_db_available

_memory_notifications = []
_memory_next_id = 1


def create_notification(user_type: str, user_id: int, title: str, message: str):
    """user_type: 'student', 'client', or 'admin'"""
    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notifications (user_type, user_id, title, message) VALUES (%s, %s, %s, %s)",
                (user_type, user_id, title, message)
            )
            conn.commit()
            new_id = cursor.lastrowid
            cursor.close()
            return new_id
        finally:
            conn.close()

    global _memory_next_id
    record = {
        "id": _memory_next_id, "user_type": user_type, "user_id": user_id,
        "title": title, "message": message, "is_read": False,
    }
    _memory_notifications.append(record)
    _memory_next_id += 1
    return record["id"]


def list_notifications(user_type: str, user_id: int, page=1, per_page=20):
    offset = (page - 1) * per_page

    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT COUNT(*) as cnt FROM notifications WHERE user_type = %s AND user_id = %s",
                (user_type, user_id)
            )
            total = cursor.fetchone()["cnt"]

            cursor.execute(
                """SELECT * FROM notifications WHERE user_type = %s AND user_id = %s
                   ORDER BY created_at DESC LIMIT %s OFFSET %s""",
                (user_type, user_id, per_page, offset)
            )
            rows = cursor.fetchall()
            cursor.close()
            return rows, total
        finally:
            conn.close()

    filtered = [r for r in _memory_notifications
                if r["user_type"] == user_type and r["user_id"] == user_id]
    total = len(filtered)
    paged = filtered[offset:offset + per_page]
    return paged, total


def count_unread(user_type: str, user_id: int) -> int:
    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM notifications WHERE user_type = %s AND user_id = %s AND is_read = FALSE",
                (user_type, user_id)
            )
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        finally:
            conn.close()

    return len([r for r in _memory_notifications
                if r["user_type"] == user_type and r["user_id"] == user_id and not r["is_read"]])


def mark_all_read(user_type: str, user_id: int):
    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE notifications SET is_read = TRUE WHERE user_type = %s AND user_id = %s",
                (user_type, user_id)
            )
            conn.commit()
            cursor.close()
        finally:
            conn.close()
        return

    for r in _memory_notifications:
        if r["user_type"] == user_type and r["user_id"] == user_id:
            r["is_read"] = True


def mark_one_read(notification_id: int) -> bool:
    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE notifications SET is_read = TRUE WHERE id = %s", (notification_id,))
            conn.commit()
            updated = cursor.rowcount > 0
            cursor.close()
            return updated
        finally:
            conn.close()

    for r in _memory_notifications:
        if r["id"] == notification_id:
            r["is_read"] = True
            return True
    return False
