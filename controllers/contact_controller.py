"""
Contact form controller — public endpoint, no authentication. Powers
the Landing Website's Contact page.
"""

import re
import models.contact as contact_model
from config.email_service import send_contact_form_notification

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def submit_contact_form(data):
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    message = (data.get("message") or data.get("description") or "").strip()

    if not name or not email or not message:
        return {
            "success": False,
            "message": "Name, email, and message are all required."
        }, 400

    if not EMAIL_REGEX.match(email):
        return {
            "success": False,
            "message": "Please provide a valid email address."
        }, 400

    if len(message) > 5000:
        return {
            "success": False,
            "message": "Message is too long (max 5000 characters)."
        }, 400

    submission_id = contact_model.create_contact_submission(name, email, message)

    email_sent = send_contact_form_notification(name, email, message)
    if email_sent:
        contact_model.mark_notified(submission_id)

    return {
        "success": True,
        "message": "Thank you for reaching out! We'll get back to you soon.",
    }, 201
