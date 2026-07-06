"""
Student controller — business logic for register/login.

Kept separate from routes so that when MySQL is added later,
only the model layer changes, not this logic.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from models.student import Student, add_student, find_by_email


def register_student(data):
    """
    Expects data = {
        "name": str,
        "email": str,
        "password": str,
        "college": str,
        "branch": str
    }
    Returns (response_dict, status_code)
    """
    required_fields = ["name", "email", "password", "college", "branch"]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return {
            "success": False,
            "message": f"Missing required field(s): {', '.join(missing)}"
        }, 400

    email = data["email"].strip().lower()

    if find_by_email(email):
        return {
            "success": False,
            "message": "An account with this email already exists."
        }, 409

    password_hash = generate_password_hash(data["password"])

    student = Student(
        name=data["name"].strip(),
        email=email,
        password_hash=password_hash,
        college=data["college"].strip(),
        branch=data["branch"].strip(),
    )
    add_student(student)

    return {
        "success": True,
        "message": "Student registered successfully.",
        "student": student.to_dict()
    }, 201


def login_student(data):
    """
    Expects data = {
        "email": str,
        "password": str
    }
    Returns (response_dict, status_code)
    """
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return {
            "success": False,
            "message": "Email and password are required."
        }, 400

    student = find_by_email(email)

    if not student or not check_password_hash(student.password_hash, password):
        return {
            "success": False,
            "message": "Invalid email or password."
        }, 401

    return {
        "success": True,
        "message": "Login successful.",
        "student": student.to_dict()
    }, 200
