"""
Database connection scaffold.

NOT wired into the app yet — students/tokens are still stored in-memory
(see models/student.py). This file exists so that when MySQL credentials
arrive, connecting the app is a small, contained change instead of a
big rewrite.

HOW TO ACTIVATE ONCE YOU HAVE CREDENTIALS:
1. Create a `.env` file in the backend/ root (see .env.example) with your
   real DB_HOST, DB_USER, DB_PASSWORD, DB_NAME.
2. Run: pip install mysql-connector-python python-dotenv
   (already listed in requirements.txt, just needs installing)
3. In models/student.py, replace the in-memory list functions
   (add_student, find_by_email, update_password, etc.) with calls to
   get_db_connection() below + real SQL queries. Keep the same function
   names/signatures so controllers/routes don't need to change.
4. In app.py, you can optionally call get_db_connection() once at
   startup to fail fast if credentials are wrong.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed yet — fine, just means .env won't
    # auto-load until it's installed (see requirements.txt).
    pass


DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "campusbridge_db"),
}


def get_db_connection():
    """
    Returns a live MySQL connection using mysql-connector-python.
    Raises an exception if credentials are missing/wrong — call this
    inside a try/except wherever it's used.

    NOTE: This function is not called anywhere yet. It's ready to use
    once the models are switched over from in-memory storage.
    """
    import mysql.connector  # imported here so the app doesn't crash
                             # on startup if the package isn't installed
                             # yet and this function is never called

    connection = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
    )
    return connection
