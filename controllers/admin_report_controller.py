"""
Reports & Analytics controller — powers the Monthly Applications chart
and Status Breakdown donut on the Reports page.
"""

from config.database import is_db_available
import models.application as application_model


def get_monthly_applications(months_back=6):
    if not is_db_available():
        return {"success": True, "monthly_data": [], "message": "Database not connected."}, 200

    rows = application_model.monthly_application_counts(months_back)
    return {"success": True, "monthly_data": rows}, 200


def get_status_breakdown():
    if not is_db_available():
        return {
            "success": True,
            "breakdown": {"Approved": 0, "Pending": 0, "Rejected": 0, "Shortlisted": 0},
            "message": "Database not connected."
        }, 200

    # "Approved" here maps to Offered, matching the donut chart labels
    # from the Reports page design (Approved/Pending/Rejected/Shortlisted).
    breakdown = {
        "Approved": application_model.count_applications_by_status("Offered"),
        "Pending": (application_model.count_applications_by_status("Applied")
                    + application_model.count_applications_by_status("In Review")),
        "Rejected": application_model.count_applications_by_status("Rejected"),
        "Shortlisted": application_model.count_applications_by_status("Shortlisted"),
    }
    return {"success": True, "breakdown": breakdown}, 200
