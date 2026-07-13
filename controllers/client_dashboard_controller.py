import models.job as job_model
import models.application as application_model


def get_dashboard_stats(client_id):
    stats = job_model.get_client_dashboard_stats(client_id)
    return {"success": True, "stats": stats}, 200


def get_recent_applications(client_id, limit=5):
    # Recent applications across ALL of this client's jobs (not one
    # specific job) — separate query, reusing the same DB helper style.
    from config.database import get_db_connection
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT a.id, a.status, a.applied_at,
                      s.name as student_name,
                      j.title as job_title
               FROM applications a
               JOIN jobs j ON a.job_id = j.id
               JOIN students s ON a.student_id = s.id
               WHERE j.client_id = %s
               ORDER BY a.applied_at DESC LIMIT %s""",
            (client_id, limit)
        )
        rows = cursor.fetchall()
        cursor.close()
        return {"success": True, "applications": rows}, 200
    finally:
        conn.close()


def get_active_jobs(client_id):
    jobs = job_model.get_active_jobs_for_client(client_id)
    return {"success": True, "jobs": jobs}, 200
