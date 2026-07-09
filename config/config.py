import os


class Config:
    """
    Central app configuration.
    No database config yet — DB_URI etc. will be added once
    the database connection task begins.
    """

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-this")
    DEBUG = os.environ.get("DEBUG", "True") == "True"
    PORT = int(os.environ.get("PORT", 5000))

    # DB_HOST = os.environ.get("DB_HOST")
    # DB_USER = os.environ.get("DB_USER")
    # DB_PASSWORD = os.environ.get("DB_PASSWORD")
    # DB_NAME = os.environ.get("DB_NAME")
