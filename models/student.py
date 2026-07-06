"""
Student model.

NOTE: No database connection yet. Students are stored in a simple
in-memory list for now. When the database task begins, replace
`students_db` and the functions below with real MySQL queries —
the function signatures (add_student, find_by_email) are written
so controllers won't need to change when that happens.
"""

# In-memory placeholder "table"
students_db = []

# Simple auto-increment counter to mimic a DB primary key
_next_id = 1


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
