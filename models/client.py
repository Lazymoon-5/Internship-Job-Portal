"""
Client (Company) model.

NOTE: No database connection yet. Clients are stored in a simple
in-memory list for now. When the database task begins, replace
`clients_db` and the functions below with real MySQL queries —
the function signatures (add_client, find_by_email, update_password)
are written so controllers won't need to change when that happens.
"""

import secrets
import datetime

# In-memory placeholder "table"
clients_db = []

# Simple auto-increment counter to mimic a DB primary key
_next_id = 1

# In-memory placeholder "table" for password reset tokens.
# Structure: { token: {"email": str, "expires_at": datetime} }
# When DB is added, this becomes a `password_resets` table.
reset_tokens = {}

RESET_TOKEN_EXPIRY_MINUTES = 30


class Client:
    def __init__(self, company_name, email, password_hash, industry, website=""):
        global _next_id
        self.id = _next_id
        _next_id += 1
        self.company_name = company_name
        self.email = email
        self.password_hash = password_hash
        self.industry = industry
        self.website = website

    def to_dict(self, include_password=False):
        data = {
            "id": self.id,
            "company_name": self.company_name,
            "email": self.email,
            "industry": self.industry,
            "website": self.website,
        }
        if include_password:
            data["password_hash"] = self.password_hash
        return data


def add_client(client: Client):
    clients_db.append(client)
    return client


def find_by_email(email: str):
    for client in clients_db:
        if client.email.lower() == email.lower():
            return client
    return None


def update_password(email: str, new_password_hash: str) -> bool:
    client = find_by_email(email)
    if not client:
        return False
    client.password_hash = new_password_hash
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
