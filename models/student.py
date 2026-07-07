"""
Student model.

NOTE: No database connection yet. Students are stored in a simple
in-memory list for now. When the database task begins, replace
`students_db` and the functions below with real MySQL queries —
the function signatures (add_student, find_by_email, update_password)
are written so controllers won't need to change when that happens.
"""

import secrets
import datetime

# In-memory placeholder "table"
students_db = []

# Simple auto-increment counter to mimic a DB primary key
_next_id = 1

# In-memory placeholder "table" for password reset tokens.
# Structure: { token: {"email": str, "expires_at": datetime} }
# When DB is added, this becomes a `password_resets` table with the
# same three fields (token, email, expires_at) plus a used/is_valid flag.
reset_tokens = {}

RESET_TOKEN_EXPIRY_MINUTES = 30


class Student:
    def __init__(self, name, email, password_hash, college, branch):
        global _next_id
        self.id = _next_id
        _next_id += 1
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.college = college
        self.branch = branch

    def to_dict(self, include_password=False):
        data = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "college": self.college,
            "branch": self.branch,
        }
        if include_password:
            data["password_hash"] = self.password_hash
        return data


def add_student(student: Student):
    students_db.append(student)
    return student


def find_by_email(email: str):
    for student in students_db:
        if student.email.lower() == email.lower():
            return student
    return None


def update_password(email: str, new_password_hash: str) -> bool:
    student = find_by_email(email)
    if not student:
        return False
    student.password_hash = new_password_hash
    return True


def create_reset_token(email: str) -> str:
    """Generates a secure token, stores it with an expiry, returns the token."""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=RESET_TOKEN_EXPIRY_MINUTES
    )
    reset_tokens[token] = {"email": email, "expires_at": expires_at}
    return token


def get_email_for_token(token: str):
    """Returns the email for a valid, unexpired token — else None."""
    entry = reset_tokens.get(token)
    if not entry:
        return None
    if datetime.datetime.utcnow() > entry["expires_at"]:
        del reset_tokens[token]
        return None
    return entry["email"]


def invalidate_token(token: str):
    reset_tokens.pop(token, None)
