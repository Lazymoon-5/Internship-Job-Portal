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
                 website="", is_verified=False):
        self.id = id
        self.company_name = company_name
        self.email = email
        self.password_hash = password_hash
        self.industry = industry
        self.website = website
        self.is_verified = bool(is_verified)

    def to_dict(self, include_password=False):
        data = {
            "id": self.id,
            "company_name": self.company_name,
            "email": self.email,
            "industry": self.industry,
            "website": self.website,
            "is_verified": self.is_verified,
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
                               "industry", "website", "is_verified"]})
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
    email = email.lower()

    if is_db_available():
        conn = get_db_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """SELECT * FROM client_otp_verifications
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
                c2.execute("UPDATE client_otp_verifications SET attempts = attempts + 1 WHERE id = %s",
                           (row["id"],))
                conn.commit()
                c2.close()
                cursor.close()
                return False, "Incorrect OTP. Please try again."

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
