"""
Database connection scaffold.

NOT wired into the app yet — clients/tokens are still stored in-memory
(see models/client.py). This file exists so that when MySQL credentials
arrive, connecting the app is a small, contained change instead of a
big rewrite.

HOW TO ACTIVATE ONCE YOU HAVE CREDENTIALS:
1. Create a `.env` file in the backend/ root (see .env.example) with your
   real DB_HOST, DB_USER, DB_PASSWORD, DB_NAME.
2. Run: pip install mysql-connector-python python-dotenv
3. In models/client.py, replace the in-memory list functions with calls
   to get_db_connection() below + real SQL queries. Keep the same
   function names/signatures so controllers/routes don't need to change.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
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
    Not called anywhere yet — ready to use once models are switched
    over from in-memory storage.
    """
    import mysql.connector

    connection = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
    )
    return connection
