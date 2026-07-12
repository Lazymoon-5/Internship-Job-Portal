"""
Seeds a test student, client, job, and application — purely for testing
the Admin backend before the real Student/Company "apply" and "post job"
APIs exist. Not meant for production use.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from werkzeug.security import generate_password_hash
import models.student as student_model
import models.client as client_model
import models.job as job_model
import models.application as application_model
from config.database import init_db

init_db()

student = student_model.add_student({
    "name": "Test Applicant", "email": "testapplicant@example.com",
    "password_hash": generate_password_hash("Test123"),
    "college": "Test College", "branch": "CSE",
})
student_model.mark_verified(student.email)
print(f"Student created: id={student.id}")

client = client_model.add_client({
    "company_name": "Test Company", "email": "testcompany@example.com",
    "password_hash": generate_password_hash("Test123"),
    "industry": "IT", "website": "https://test.com",
})
client_model.update_admin_status(client.id, "Approved")
print(f"Client created: id={client.id}")

job_id = job_model.create_job({
    "client_id": client.id, "title": "Software Engineer Intern",
    "description": "Great internship opportunity.",
    "job_type": "Internship", "required_skills": "Python, React",
    "eligibility_criteria": "CGPA 7+", "location": "Remote",
    "salary_stipend": "15000/month", "last_date_to_apply": "2026-12-31",
})
print(f"Job created: id={job_id}")

app_id = application_model.create_application({
    "student_id": student.id, "job_id": job_id,
    "cover_letter": "I am very interested in this role.",
    "portfolio_link": "https://github.com/test",
})
print(f"Application created: id={app_id}")

print("\nSeed complete.")
