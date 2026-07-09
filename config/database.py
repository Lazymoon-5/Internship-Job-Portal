"""
Database connection module — MySQL, using mysql-connector-python.

DB_CONFIGURED (below) auto-detects whether real credentials are present
in .env. If DB_HOST is blank, or a connection attempt fails, the app
falls back to in-memory storage (see models/student.py and
models/client.py) so the rest of the app — OTP, email, Google login —
can still be tested while waiting on real database credentials. Once
real credentials are added, this switches to MySQL automatically, no
code changes needed.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "").strip(),
    "port": int(os.environ.get("DB_PORT", 3306) or 3306),
    "user": os.environ.get("DB_USER", "").strip(),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "").strip(),
    "charset": os.environ.get("DB_CHARSET", "utf8mb4"),
}

DB_CONFIGURED = bool(DB_CONFIG["host"])

_pool = None
_connection_verified = False
_connection_failed = False


def is_db_available() -> bool:
    global _connection_verified, _connection_failed

    if not DB_CONFIGURED:
        return False
    if _connection_verified:
        return True
    if _connection_failed:
        return False

    try:
        conn = get_db_connection()
        conn.close()
        _connection_verified = True
        return True
    except Exception as e:
        print(f"[DB] Not reachable ({e}) — falling back to in-memory storage.")
        _connection_failed = True
        return False


def get_pool():
    _pool = pooling.MySQLConnectionPool(
    pool_name="placify_pool",
    pool_size=5,
    host=DB_CONFIG["host"],
    port=DB_CONFIG["port"],
    user=DB_CONFIG["user"],
    password=DB_CONFIG["password"],
    database=DB_CONFIG["database"],
    charset=DB_CONFIG["charset"],
    connection_timeout=5,

    ssl_disabled=False
    )
    return _pool


def get_db_connection():
    return get_pool().get_connection()


def init_db():
    if not is_db_available():
        print("[DB] Skipping table creation — DB not configured/reachable. "
              "Using in-memory storage for now.")
        return

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                email VARCHAR(150) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                college VARCHAR(200) NOT NULL,
                branch VARCHAR(100) NOT NULL,
                is_verified BOOLEAN DEFAULT FALSE,
                google_id VARCHAR(255) DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(150) NOT NULL,
                token VARCHAR(255) NOT NULL UNIQUE,
                expires_at DATETIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS otp_verifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(150) NOT NULL,
                otp_code VARCHAR(10) NOT NULL,
                purpose VARCHAR(50) NOT NULL,
                expires_at DATETIME NOT NULL,
                is_used BOOLEAN DEFAULT FALSE,
                attempts INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company_name VARCHAR(150) NOT NULL,
                email VARCHAR(150) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                industry VARCHAR(150) NOT NULL,
                website VARCHAR(255) DEFAULT NULL,
                is_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS client_password_resets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(150) NOT NULL,
                token VARCHAR(255) NOT NULL UNIQUE,
                expires_at DATETIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS client_otp_verifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(150) NOT NULL,
                otp_code VARCHAR(10) NOT NULL,
                purpose VARCHAR(50) NOT NULL,
                expires_at DATETIME NOT NULL,
                is_used BOOLEAN DEFAULT FALSE,
                attempts INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
        cursor.close()
        print("[DB] Connected and tables verified.")
    finally:
        conn.close()
