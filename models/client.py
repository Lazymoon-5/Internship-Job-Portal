"""
Client (Company) model — automatically uses real MySQL if available,
otherwise falls back to in-memory storage (reset on server restart).
Mirrors models/student.py exactly, but for the Client/Company entity —
so this can be tested right now (OTP/email) while waiting on real DB
credentials, and switches to MySQL automatically once .env is filled in.
"""

import secrets
import datetime
from config.database import get_db_connection, is_db_available

# ---------------- In-memory fallback storage ----------------
_memory_clients = []         # list of dicts
_memory_next_id = 1
_memory_reset_tokens = {}    # token -> {email, expires_at}
_memory_otps = {}            # (email, purpose) -> {otp_code, expires_at, is_used, attempts}


class Client:
    def __init__(self, id, company_name, email, password_hash, industry,
                 website="", is_verified=False, admin_status="Pending"):
        self.id = id
        self.company_name = company_name
        self.email = email
        self.password_hash = password_hash
        self.industry = industry
        self.website = website
        self.is_verified = bool(is_verified)
        self.admin_status = admin_status or "Pending"

    def to_dict(self, include_password=False):
        data = {
            "id": self.id,
            "company_name": self.company_name,
            "email": self.email,
            "industry": self.industry,
            "website": self.website,
            "is_verified": self.is_verified,
            "admin_status": self.admin_status,
        }
        if include_password:
            data["password_hash"] = self.password_hash
        return data


# ================= Clients =================

def add_client(client_data: dict):
    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO clients (company_name, email, password_hash, industry, website)
                   VALUES (%s, %s, %s, %s, %s)""",
                (client_data["company_name"], client_data["email"],
                 client_data["password_hash"], client_data["industry"],
                 client_data.get("website", ""))
            )
            conn.commit()
            new_id = cursor.lastrowid
            cursor.close()
            return Client(id=new_id, **client_data)
        finally:
            conn.close()

    # --- in-memory fallback ---
    global _memory_next_id
    record = {
        "id": _memory_next_id, "company_name": client_data["company_name"],
        "email": client_data["email"], "password_hash": client_data["password_hash"],
        "industry": client_data["industry"], "website": client_data.get("website", ""),
        "is_verified": False,
    }
    _memory_clients.append(record)
    _memory_next_id += 1
    return Client(**record)


def find_by_email(email: str):
    email = email.lower()

    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM clients WHERE email = %s", (email,))
            row = cursor.fetchone()
            cursor.close()
            if not row:
                return None
            return Client(**{k: row[k] for k in
                              ["id", "company_name", "email", "password_hash",
                               "industry", "website", "is_verified", "admin_status"]})
        finally:
            conn.close()

    # --- in-memory fallback ---
    for record in _memory_clients:
        if record["email"].lower() == email:
            return Client(**record)
    return None


def update_password(email: str, new_password_hash: str) -> bool:
    email = email.lower()

    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE clients SET password_hash = %s WHERE email = %s",
                (new_password_hash, email)
            )
            conn.commit()
            updated = cursor.rowcount > 0
            cursor.close()
            return updated
        finally:
            conn.close()

    # --- in-memory fallback ---
    for record in _memory_clients:
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
                "UPDATE clients SET is_verified = TRUE WHERE email = %s",
                (email,)
            )
            conn.commit()
            updated = cursor.rowcount > 0
            cursor.close()
            return updated
        finally:
            conn.close()

    # --- in-memory fallback ---
    for record in _memory_clients:
        if record["email"].lower() == email:
            record["is_verified"] = True
            return True
    return False


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
                "INSERT INTO client_password_resets (email, token, expires_at) VALUES (%s, %s, %s)",
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
            cursor.execute("SELECT * FROM client_password_resets WHERE token = %s", (token,))
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
            cursor.execute("DELETE FROM client_password_resets WHERE token = %s", (token,))
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
                "DELETE FROM client_otp_verifications WHERE email = %s AND purpose = %s",
                (email, purpose)
            )
            cursor.execute(
                """INSERT INTO client_otp_verifications (email, otp_code, purpose, expires_at)
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
    email = (email or "").strip().lower()
    otp_code = str(otp_code or "").strip()

    if is_db_available():
        try:
            conn = get_db_connection()
        except Exception as db_err:
            print(f"[VERIFY OTP DB CONN ERROR] {db_err}")
            return False, "Database server busy. Please click Verify OTP again."

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """SELECT * FROM client_otp_verifications
                   WHERE email = %s AND purpose = %s
                   ORDER BY created_at DESC LIMIT 1""",
                (email, purpose)
            )
            row = cursor.fetchone()

            if not row:
                cursor.close()
                return False, "No OTP request found. Please request a new one."

            stored_code = str(row["otp_code"]).strip()

            if row.get("is_used"):
                if stored_code == otp_code:
                    cursor.close()
                    return True, "OTP verified successfully."
                cursor.close()
                return False, "This OTP has already been used. Please request a new one."

            if row["attempts"] >= OTP_MAX_ATTEMPTS:
                cursor.close()
                return False, "Too many incorrect attempts. Please request a new OTP."

            if stored_code != otp_code:
                c2 = conn.cursor()
                c2.execute("UPDATE client_otp_verifications SET attempts = attempts + 1 WHERE id = %s",
                           (row["id"],))
                conn.commit()
                c2.close()
                cursor.close()
                return False, "Incorrect OTP code. Please check and try again."

            c2 = conn.cursor()
            c2.execute("UPDATE client_otp_verifications SET is_used = TRUE WHERE id = %s", (row["id"],))
            conn.commit()
            c2.close()
            cursor.close()
            return True, "OTP verified successfully."
        finally:
            conn.close()

    # --- in-memory fallback ---
    entry = _memory_otps.get((email, purpose))
    if not entry:
        return False, "No OTP request found. Please request a new one."
    stored_code = str(entry["otp_code"]).strip()
    if entry.get("is_used"):
        if stored_code == otp_code:
            return True, "OTP verified successfully."
        return False, "This OTP has already been used. Please request a new one."
    if entry["attempts"] >= OTP_MAX_ATTEMPTS:
        return False, "Too many incorrect attempts. Please request a new OTP."
    if stored_code != otp_code:
        entry["attempts"] += 1
        return False, "Incorrect OTP code. Please check and try again."
    entry["is_used"] = True
    return True, "OTP verified successfully."


# ================= Admin management functions =================

def list_clients(search="", status_filter="", page=1, per_page=10):
    offset = (page - 1) * per_page

    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            where_clauses = []
            params = []

            if search:
                where_clauses.append("(company_name LIKE %s OR industry LIKE %s OR email LIKE %s)")
                like = f"%{search}%"
                params.extend([like, like, like])

            if status_filter:
                where_clauses.append("admin_status = %s")
                params.append(status_filter)

            where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

            cursor.execute(f"SELECT COUNT(*) as cnt FROM clients {where_sql}", params)
            total = cursor.fetchone()["cnt"]

            cursor.execute(
                f"SELECT * FROM clients {where_sql} ORDER BY created_at DESC LIMIT %s OFFSET %s",
                params + [per_page, offset]
            )
            rows = cursor.fetchall()
            cursor.close()

            clients = [Client(
                id=r["id"], company_name=r["company_name"], email=r["email"],
                password_hash=r["password_hash"], industry=r["industry"],
                website=r["website"], is_verified=r["is_verified"],
                admin_status=r["admin_status"]
            ).to_dict() for r in rows]
            return clients, total
        finally:
            conn.close()

    filtered = _memory_clients
    if search:
        s = search.lower()
        filtered = [r for r in filtered if s in r["company_name"].lower()
                    or s in r["email"].lower() or s in r.get("industry", "").lower()]
    if status_filter:
        filtered = [r for r in filtered if r.get("admin_status", "Pending") == status_filter]
    total = len(filtered)
    paged = filtered[offset:offset + per_page]
    return [Client(**r).to_dict() for r in paged], total


def find_by_id(client_id: int):
    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM clients WHERE id = %s", (client_id,))
            row = cursor.fetchone()
            cursor.close()
            if not row:
                return None
            return Client(id=row["id"], company_name=row["company_name"], email=row["email"],
                          password_hash=row["password_hash"], industry=row["industry"],
                          website=row["website"], is_verified=row["is_verified"],
                          admin_status=row["admin_status"])
        finally:
            conn.close()

    for record in _memory_clients:
        if record["id"] == client_id:
            return Client(**record)
    return None


def update_admin_status(client_id: int, status: str) -> bool:
    """status: 'Pending', 'Approved', 'Rejected', or 'Blocked'"""
    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE clients SET admin_status = %s WHERE id = %s", (status, client_id))
            conn.commit()
            updated = cursor.rowcount > 0
            cursor.close()
            return updated
        finally:
            conn.close()

    for record in _memory_clients:
        if record["id"] == client_id:
            record["admin_status"] = status
            return True
    return False


def delete_client(client_id: int) -> bool:
    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients WHERE id = %s", (client_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
            cursor.close()
            return deleted
        finally:
            conn.close()

    global _memory_clients
    before = len(_memory_clients)
    _memory_clients = [r for r in _memory_clients if r["id"] != client_id]
    return len(_memory_clients) < before


def count_clients() -> int:
    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM clients")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        finally:
            conn.close()
    return len(_memory_clients)
