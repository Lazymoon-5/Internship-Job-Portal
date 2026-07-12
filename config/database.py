"""
Database connection module — MySQL, using mysql-connector-python.
Auto-falls back to in-memory storage if DB isn't configured/reachable.
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
    global _pool
    if _pool is None:
        from mysql.connector import pooling
        _pool = pooling.MySQLConnectionPool(
            pool_name="placify_pool", pool_size=5,
            host=DB_CONFIG["host"], port=DB_CONFIG["port"],
            user=DB_CONFIG["user"], password=DB_CONFIG["password"],
            database=DB_CONFIG["database"], charset=DB_CONFIG["charset"],
            connection_timeout=5,
        )
    return _pool


def get_db_connection():
    return get_pool().get_connection()


def init_db():
    if not is_db_available():
        print("[DB] Skipping table creation — DB not configured/reachable. Using in-memory storage.")
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
                status ENUM('Active','Blocked') DEFAULT 'Active',
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
                admin_status ENUM('Pending','Approved','Rejected','Blocked') DEFAULT 'Pending',
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                email VARCHAR(150) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                client_id INT NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                job_type ENUM('Internship','Full-Time') DEFAULT 'Internship',
                required_skills TEXT,
                eligibility_criteria TEXT,
                location VARCHAR(150),
                salary_stipend VARCHAR(100),
                last_date_to_apply DATE,
                status ENUM('Pending','Approved','Rejected','Closed') DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                job_id INT NOT NULL,
                resume_id INT DEFAULT NULL,
                cover_letter TEXT,
                portfolio_link VARCHAR(255),
                status ENUM('Applied','In Review','Shortlisted','Interview','Offered','Rejected') DEFAULT 'Applied',
                admin_notes TEXT,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
                UNIQUE KEY unique_application (student_id, job_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_type ENUM('student','client','admin') NOT NULL,
                user_id INT NOT NULL,
                title VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                filename VARCHAR(255) NOT NULL,
                file_url VARCHAR(500) NOT NULL,
                is_primary BOOLEAN DEFAULT FALSE,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS certifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                certificate_name VARCHAR(200) NOT NULL,
                issued_by VARCHAR(200),
                file_url VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                skill_name VARCHAR(100) NOT NULL,
                level VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        conn.commit()
        cursor.close()

        # ---- Safe ALTER TABLE for new student profile columns ----
        # Wrapped individually so this works whether run against a
        # brand-new database (columns won't exist, ALTER succeeds) or
        # an existing one from before this update (ALTER may fail with
        # "duplicate column" — caught and ignored, since that just means
        # it was already added in a previous run).
        profile_columns = [
            ("department", "VARCHAR(150)"),
            ("current_year", "VARCHAR(50)"),
            ("mobile_no", "VARCHAR(20)"),
            ("profile_summary", "TEXT"),
            ("city", "VARCHAR(100)"),
            ("pincode", "VARCHAR(20)"),
            ("state", "VARCHAR(100)"),
            ("linkedin_url", "VARCHAR(255)"),
            ("enrollment_no", "VARCHAR(100)"),
            ("college_address", "TEXT"),
            ("course", "VARCHAR(150)"),
            ("gpa_cgpa", "VARCHAR(20)"),
            ("profile_photo_url", "VARCHAR(500)"),
            ("profile_completed", "BOOLEAN DEFAULT FALSE"),
        ]
        conn2 = get_db_connection()
        try:
            cursor2 = conn2.cursor()
            for col_name, col_type in profile_columns:
                try:
                    cursor2.execute(f"ALTER TABLE students ADD COLUMN {col_name} {col_type}")
                    conn2.commit()
                except Exception:
                    conn2.rollback()  # column already exists — fine, skip it
            cursor2.close()
        finally:
            conn2.close()

        print("[DB] Connected and tables verified.")
    finally:
        conn.close()
