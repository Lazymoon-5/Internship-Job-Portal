"""
Dashboard Overview controller — powers the stat cards and
"Recent Applications" list on the Admin Dashboard home page.
"""

from config.database import is_db_available
import models.student as student_model
import models.client as client_model
import models.job as job_model
import models.application as application_model


def get_dashboard_stats():
    if not is_db_available():
        return {
            "success": True,
            "message": "Database not connected — showing zeroed stats (in-memory mode has no jobs/applications support).",
            "stats": {
                "total_students": student_model.count_students(),
                "total_companies": client_model.count_clients(),
                "total_job_posts": 0,
                "total_applications": 0,
            }
        }, 200

    return {
        "success": True,
        "stats": {
            "total_students": student_model.count_students(),
            "total_companies": client_model.count_clients(),
            "total_job_posts": job_model.count_jobs(),
            "total_applications": application_model.count_applications(),
        }
    }, 200


def get_recent_applications(limit=5):
    if not is_db_available():
        return {
            "success": True,
            "applications": [],
            "message": "Database not connected — no application data available in in-memory mode."
        }, 200

    rows, _ = application_model.list_applications(page=1, per_page=limit)
    return {"success": True, "applications": rows}, 200
