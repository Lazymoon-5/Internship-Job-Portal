"""
One-time (or occasional) script to create an admin account.

This is deliberately NOT an API route — admins should never be
publicly creatable over the internet. Run this manually, locally,
whenever a new admin needs an account:

    python scripts/seed_admin.py

It will prompt for name, email, and password, hash the password, and
insert the admin directly into the database (or in-memory store, if
DB isn't configured — though in that case it won't survive a restart,
so make sure your .env DB credentials are set before running this for
real use).
"""

import sys
import os
import getpass

# Allow running this script directly from the scripts/ folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from werkzeug.security import generate_password_hash
from models.admin import add_admin, find_by_email
from config.database import is_db_available, init_db


def main():
    print("=== Create Admin Account ===")

    try:
        init_db()
    except Exception as e:
        print(f"[DB] Could not initialize tables: {e}")

    if not is_db_available():
        print("⚠️  WARNING: No database configured/reachable — this admin")
        print("   will only exist in memory and disappear when the server")
        print("   restarts. Set up your .env DB credentials first for a")
        print("   real, persistent admin account.\n")
        proceed = input("Continue anyway? (y/n): ").strip().lower()
        if proceed != "y":
            print("Cancelled.")
            return

    name = input("Admin name: ").strip()
    email = input("Admin email: ").strip().lower()

    if find_by_email(email):
        print(f"\n❌ An admin with email '{email}' already exists. Aborting.")
        return

    password = getpass.getpass("Admin password (hidden while typing): ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("\n❌ Passwords don't match. Aborting.")
        return

    if len(password) < 6:
        print("\n❌ Password must be at least 6 characters. Aborting.")
        return

    password_hash = generate_password_hash(password)
    admin = add_admin({"name": name, "email": email, "password_hash": password_hash})

    print(f"\n✅ Admin account created: {admin.name} <{admin.email}> (id={admin.id})")
    print("You can now log in via POST /api/admin/login with this email/password.")


if __name__ == "__main__":
    main()
