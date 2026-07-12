"""
Student model — automatically uses real MySQL if available, otherwise
falls back to in-memory storage (reset on server restart). This lets
OTP/email/Google-login be tested right now while waiting on real DB
credentials, and switches to MySQL automatically once they're added —
no code changes needed, just update .env.

Every public function below has the exact same name/signature either
way, so controllers never need to know or care which mode is active.
"""

import secrets
import datetime
from config.database import get_db_connection, is_db_available

# ---------------- In-memory fallback storage ----------------
_memory_students = []       # list of dicts
_memory_next_id = 1
_memory_reset_tokens = {}   # token -> {email, expires_at}
_memory_otps = {}           # (email, purpose) -> {otp_code, expires_at, is_used, attempts}


class Student:
    def __init__(self, id, name, email, password_hash, college, branch,
                 is_verified=False, google_id=None, status="Active"):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.college = college
        self.branch = branch
        self.is_verified = bool(is_verified)
        self.google_id = google_id
        self.status = status or "Active"

    def to_dict(self, include_password=False):
        data = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "college": self.college,
            "branch": self.branch,
            "is_verified": self.is_verified,
            "status": self.status,
        }
        if include_password:
            data["password_hash"] = self.password_hash
        return data


# ================= Students =================

def add_student(student_data: dict):
    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO students (name, email, password_hash, college, branch)
                   VALUES (%s, %s, %s, %s, %s)""",
                (student_data["name"], student_data["email"],
                 student_data["password_hash"], student_data["college"],
                 student_data["branch"])
            )
            conn.commit()
            new_id = cursor.lastrowid
            cursor.close()
            return Student(id=new_id, **student_data)
        finally:
            conn.close()

    # --- in-memory fallback ---
    global _memory_next_id
    record = {
        "id": _memory_next_id, "name": student_data["name"],
        "email": student_data["email"], "password_hash": student_data["password_hash"],
        "college": student_data["college"], "branch": student_data["branch"],
        "is_verified": False, "google_id": None,
    }
    _memory_students.append(record)
    _memory_next_id += 1
    return Student(**record)


def find_by_email(email: str):
    email = email.lower()

    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM students WHERE email = %s", (email,))
            row = cursor.fetchone()
            cursor.close()
            if not row:
                return None
            return Student(**{k: row[k] for k in
                               ["id", "name", "email", "password_hash", "college",
                                "branch", "is_verified", "google_id", "status"]})
        finally:
            conn.close()

    # --- in-memory fallback ---
    for record in _memory_students:
        if record["email"].lower() == email:
            return Student(**record)
    return None


def update_password(email: str, new_password_hash: str) -> bool:
    email = email.lower()

    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE students SET password_hash = %s WHERE email = %s",
                (new_password_hash, email)
            )
            conn.commit()
            updated = cursor.rowcount > 0
            cursor.close()
            return updated
        finally:
            conn.close()

    # --- in-memory fallback ---
    for record in _memory_students:
        if record["email"].lower() == email:
            record["password_hash"] = new_password_hash
            return True
    return False


def mark_verified(email: str) -> bool:
    email = email.lower()

    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE students SET is_verified = TRUE WHERE email = %s",
                (email,)
            )
            conn.commit()
            updated = cursor.rowcount > 0
            cursor.close()
            return updated
        finally:
            conn.close()

    # --- in-memory fallback ---
    for record in _memory_students:
        if record["email"].lower() == email:
            record["is_verified"] = True
            return True
    return False


def find_or_create_by_google(google_id: str, email: str, name: str):
    email = email.lower()

    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM students WHERE google_id = %s OR email = %s",
                (google_id, email)
            )
            row = cursor.fetchone()

            if row:
                if not row["google_id"]:
                    c2 = conn.cursor()
                    c2.execute("UPDATE students SET google_id = %s WHERE id = %s",
                               (google_id, row["id"]))
                    conn.commit()
                    c2.close()
                cursor.close()
                return Student(id=row["id"], name=row["name"], email=row["email"],
                               password_hash=row["password_hash"], college=row["college"],
                               branch=row["branch"], is_verified=row["is_verified"],
                               google_id=google_id)

            placeholder_hash = secrets.token_hex(32)
            cursor.execute(
                """INSERT INTO students (name, email, password_hash, college, branch, is_verified, google_id)
                   VALUES (%s, %s, %s, '', '', TRUE, %s)""",
                (name, email, placeholder_hash, google_id)
            )
            conn.commit()
            new_id = cursor.lastrowid
            cursor.close()
            return Student(id=new_id, name=name, email=email, password_hash=placeholder_hash,
                           college="", branch="", is_verified=True, google_id=google_id)
        finally:
            conn.close()

    # --- in-memory fallback ---
    global _memory_next_id
    for record in _memory_students:
        if record.get("google_id") == google_id or record["email"].lower() == email:
            record["google_id"] = google_id
            return Student(**record)

    placeholder_hash = secrets.token_hex(32)
    record = {
        "id": _memory_next_id, "name": name, "email": email,
        "password_hash": placeholder_hash, "college": "", "branch": "",
        "is_verified": True, "google_id": google_id,
    }
    _memory_students.append(record)
    _memory_next_id += 1
    return Student(**record)


# ================= Password reset tokens =================

RESET_TOKEN_EXPIRY_MINUTES = 30


def create_reset_token(email: str) -> str:
    email = email.lower()
    token = secrets.token_urlsafe(32)
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=RESET_TOKEN_EXPIRY_MINUTES)

    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO password_resets (email, token, expires_at) VALUES (%s, %s, %s)",
                (email, token, expires_at)
            )
            conn.commit()
            cursor.close()
            return token
        finally:
            conn.close()

    # --- in-memory fallback ---
    _memory_reset_tokens[token] = {"email": email, "expires_at": expires_at}
    return token


def get_email_for_token(token: str):
    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM password_resets WHERE token = %s", (token,))
            row = cursor.fetchone()
            cursor.close()
            if not row:
                return None
            if datetime.datetime.utcnow() > row["expires_at"]:
                invalidate_token(token)
                return None
            return row["email"]
        finally:
            conn.close()

    # --- in-memory fallback ---
    entry = _memory_reset_tokens.get(token)
    if not entry:
        return None
    if datetime.datetime.utcnow() > entry["expires_at"]:
        del _memory_reset_tokens[token]
        return None
    return entry["email"]


def invalidate_token(token: str):
    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM password_resets WHERE token = %s", (token,))
            conn.commit()
            cursor.close()
        finally:
            conn.close()
        return

    # --- in-memory fallback ---
    _memory_reset_tokens.pop(token, None)


# ================= OTP verification =================

OTP_EXPIRY_MINUTES = 10
OTP_MAX_ATTEMPTS = 5


def create_otp(email: str, purpose: str = "registration") -> str:
    email = email.lower()
    otp_code = f"{secrets.randbelow(1000000):06d}"
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=OTP_EXPIRY_MINUTES)

    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM otp_verifications WHERE email = %s AND purpose = %s",
                (email, purpose)
            )
            cursor.execute(
                """INSERT INTO otp_verifications (email, otp_code, purpose, expires_at)
                   VALUES (%s, %s, %s, %s)""",
                (email, otp_code, purpose, expires_at)
            )
            conn.commit()
            cursor.close()
            return otp_code
        finally:
            conn.close()

    # --- in-memory fallback ---
    _memory_otps[(email, purpose)] = {
        "otp_code": otp_code, "expires_at": expires_at,
        "is_used": False, "attempts": 0,
    }
    return otp_code


def verify_otp(email: str, otp_code: str, purpose: str = "registration"):
    email = email.lower()

    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """SELECT * FROM otp_verifications
                   WHERE email = %s AND purpose = %s AND is_used = FALSE
                   ORDER BY created_at DESC LIMIT 1""",
                (email, purpose)
            )
            row = cursor.fetchone()

            if not row:
                cursor.close()
                return False, "No OTP request found. Please request a new one."
            if datetime.datetime.utcnow() > row["expires_at"]:
                cursor.close()
                return False, "OTP has expired. Please request a new one."
            if row["attempts"] >= OTP_MAX_ATTEMPTS:
                cursor.close()
                return False, "Too many incorrect attempts. Please request a new OTP."
            if row["otp_code"] != otp_code:
                c2 = conn.cursor()
                c2.execute("UPDATE otp_verifications SET attempts = attempts + 1 WHERE id = %s",
                           (row["id"],))
                conn.commit()
                c2.close()
                cursor.close()
                return False, "Incorrect OTP. Please try again."

            c2 = conn.cursor()
            c2.execute("UPDATE otp_verifications SET is_used = TRUE WHERE id = %s", (row["id"],))
            conn.commit()
            c2.close()
            cursor.close()
            return True, "OTP verified successfully."
        finally:
            conn.close()

    # --- in-memory fallback ---
    entry = _memory_otps.get((email, purpose))
    if not entry or entry["is_used"]:
        return False, "No OTP request found. Please request a new one."
    if datetime.datetime.utcnow() > entry["expires_at"]:
        return False, "OTP has expired. Please request a new one."
    if entry["attempts"] >= OTP_MAX_ATTEMPTS:
        return False, "Too many incorrect attempts. Please request a new OTP."
    if entry["otp_code"] != otp_code:
        entry["attempts"] += 1
        return False, "Incorrect OTP. Please try again."
    entry["is_used"] = True
    return True, "OTP verified successfully."


# ================= Admin management functions =================

def list_students(search="", status_filter="", page=1, per_page=10):
    """
    Returns (list_of_students_as_dicts, total_count).
    search matches against name, college, or email (case-insensitive).
    status_filter: "" (all), "Active", or "Blocked".
    """
    offset = (page - 1) * per_page

    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            where_clauses = []
            params = []

            if search:
                where_clauses.append("(name LIKE %s OR college LIKE %s OR email LIKE %s)")
                like = f"%{search}%"
                params.extend([like, like, like])

            if status_filter:
                where_clauses.append("status = %s")
                params.append(status_filter)

            where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

            cursor.execute(f"SELECT COUNT(*) as cnt FROM students {where_sql}", params)
            total = cursor.fetchone()["cnt"]

            cursor.execute(
                f"SELECT * FROM students {where_sql} ORDER BY created_at DESC LIMIT %s OFFSET %s",
                params + [per_page, offset]
            )
            rows = cursor.fetchall()
            cursor.close()

            students = [Student(
                id=r["id"], name=r["name"], email=r["email"], password_hash=r["password_hash"],
                college=r["college"], branch=r["branch"], is_verified=r["is_verified"],
                google_id=r["google_id"], status=r["status"]
            ).to_dict() for r in rows]
            return students, total
        finally:
            conn.close()

    # --- in-memory fallback ---
    filtered = _memory_students
    if search:
        s = search.lower()
        filtered = [r for r in filtered if s in r["name"].lower() or s in r["email"].lower()
                    or s in r.get("college", "").lower()]
    if status_filter:
        filtered = [r for r in filtered if r.get("status", "Active") == status_filter]
    total = len(filtered)
    paged = filtered[offset:offset + per_page]
    return [Student(**r).to_dict() for r in paged], total


def find_by_id(student_id: int):
    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
            row = cursor.fetchone()
            cursor.close()
            if not row:
                return None
            return Student(id=row["id"], name=row["name"], email=row["email"],
                           password_hash=row["password_hash"], college=row["college"],
                           branch=row["branch"], is_verified=row["is_verified"],
                           google_id=row["google_id"], status=row["status"])
        finally:
            conn.close()

    for record in _memory_students:
        if record["id"] == student_id:
            return Student(**record)
    return None


def update_status(student_id: int, status: str) -> bool:
    """status must be 'Active' or 'Blocked'"""
    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE students SET status = %s WHERE id = %s", (status, student_id))
            conn.commit()
            updated = cursor.rowcount > 0
            cursor.close()
            return updated
        finally:
            conn.close()

    for record in _memory_students:
        if record["id"] == student_id:
            record["status"] = status
            return True
    return False


def delete_student(student_id: int) -> bool:
    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
            cursor.close()
            return deleted
        finally:
            conn.close()

    global _memory_students
    before = len(_memory_students)
    _memory_students = [r for r in _memory_students if r["id"] != student_id]
    return len(_memory_students) < before


def count_students() -> int:
    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM students")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        finally:
            conn.close()
    return len(_memory_students)
