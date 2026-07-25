"""
Admin model — automatically uses real MySQL if available, otherwise
falls back to in-memory storage. Mirrors models/student.py and
models/client.py in pattern, but Admin has NO public registration —
accounts are only created via scripts/seed_admin.py (run manually,
not exposed as an API route), since admins are trusted operators, not
public sign-ups.
"""

from config.database import get_db_connection, is_db_available

_memory_admins = []
_memory_next_id = 1


class Admin:
    def __init__(self, id, name, email, password_hash):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash

    def to_dict(self, include_password=False):
        data = {"id": self.id, "name": self.name, "email": self.email}
        if include_password:
            data["password_hash"] = self.password_hash
        return data


def add_admin(admin_data: dict):
    """Used only by scripts/seed_admin.py — not exposed via any API route."""
    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO admins (name, email, password_hash) VALUES (%s, %s, %s)",
                (admin_data["name"], admin_data["email"], admin_data["password_hash"])
            )
            conn.commit()
            new_id = cursor.lastrowid
            cursor.close()
            return Admin(id=new_id, **admin_data)
        finally:
            conn.close()

    global _memory_next_id
    record = {
        "id": _memory_next_id, "name": admin_data["name"],
        "email": admin_data["email"], "password_hash": admin_data["password_hash"],
    }
    _memory_admins.append(record)
    _memory_next_id += 1
    return Admin(**record)


def find_by_email(email: str):
    email = email.lower()

    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM admins WHERE email = %s", (email,))
            row = cursor.fetchone()
            cursor.close()
            if not row:
                return None
            return Admin(id=row["id"], name=row["name"], email=row["email"],
                         password_hash=row["password_hash"])
        finally:
            conn.close()

    for record in _memory_admins:
        if record["email"].lower() == email:
            return Admin(**record)
    return None


def find_by_id(admin_id: int):
    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM admins WHERE id = %s", (admin_id,))
            row = cursor.fetchone()
            cursor.close()
            if not row:
                return None
            return Admin(id=row["id"], name=row["name"], email=row["email"],
                         password_hash=row["password_hash"])
        finally:
            conn.close()

    for record in _memory_admins:
        if record["id"] == admin_id:
            return Admin(**record)
    return None


def update_password(admin_id: int, new_password_hash: str) -> bool:
    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE admins SET password_hash = %s WHERE id = %s",
                (new_password_hash, admin_id)
            )
            conn.commit()
            updated = cursor.rowcount > 0
            cursor.close()
            return updated
        finally:
            conn.close()

    for record in _memory_admins:
        if record["id"] == admin_id:
            record["password_hash"] = new_password_hash
            return True
    return False


def list_all_admin_ids():
    """Returns a list of every admin's id — used to broadcast a
    notification to all admins at once (e.g. new student verified,
    new job awaiting approval), since notifications are per-admin."""
    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM admins")
            ids = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return ids
        finally:
            conn.close()

    return [record["id"] for record in _memory_admins]
