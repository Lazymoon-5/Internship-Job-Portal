"""
Manage Companies controller — list/search/filter, approve/reject/block, delete.
"""

import models.client as client_model
import models.notification as notification_model


def get_companies(args):
    search = args.get("search", "").strip()
    status_filter = args.get("status", "").strip()
    page = int(args.get("page", 1))
    per_page = int(args.get("per_page", 10))

    clients, total = client_model.list_clients(search, status_filter, page, per_page)

    return {
        "success": True,
        "companies": clients,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if per_page else 1,
    }, 200


import models.client_profile as client_profile_model
from config.database import get_db_connection


def get_company_detail(client_id):
    company = client_profile_model.get_profile(client_id)
    if not company:
        client = client_model.find_by_id(client_id)
        if not client:
            return {"success": False, "message": "Company not found."}, 404
        company = client.to_dict()

    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        # 1. Total Job Posts count
        cursor.execute("SELECT COUNT(*) as cnt FROM jobs WHERE client_id = %s", (client_id,))
        total_job_posts = (cursor.fetchone() or {}).get("cnt", 0)

        # 2. Total Applications received count
        cursor.execute(
            """SELECT COUNT(*) as cnt
               FROM applications a
               JOIN jobs j ON a.job_id = j.id
               WHERE j.client_id = %s""",
            (client_id,)
        )
        total_applications = (cursor.fetchone() or {}).get("cnt", 0)

        # 3. Hired Students count
        cursor.execute(
            """SELECT COUNT(*) as cnt
               FROM applications a
               JOIN jobs j ON a.job_id = j.id
               WHERE j.client_id = %s AND (
                   LOWER(a.status) = 'hired' OR
                   LOWER(a.status) = 'selected' OR
                   LOWER(a.status) = 'shortlisted'
               )""",
            (client_id,)
        )
        hired_students = (cursor.fetchone() or {}).get("cnt", 0)

        # 4. Pending Reviews count
        cursor.execute(
            """SELECT COUNT(*) as cnt
               FROM applications a
               JOIN jobs j ON a.job_id = j.id
               WHERE j.client_id = %s AND (
                   LOWER(a.status) = 'applied' OR
                   LOWER(a.status) = 'pending' OR
                   a.viewed_by_company = FALSE
               )""",
            (client_id,)
        )
        pending_reviews = (cursor.fetchone() or {}).get("cnt", 0)

        # 5. Recent Job Posts list
        cursor.execute(
            """SELECT j.id, j.title, j.job_type, j.location, j.salary_min, j.salary_max,
                      j.salary_stipend, j.status, j.created_at,
                      (SELECT COUNT(*) FROM applications WHERE job_id = j.id) as applications_count
               FROM jobs j
               WHERE j.client_id = %s
               ORDER BY j.created_at DESC
               LIMIT 10""",
            (client_id,)
        )
        job_posts = cursor.fetchall() or []
        cursor.close()

        company["name"] = company.get("company_name") or company.get("name") or "Company"
        company["status"] = company.get("admin_status") or company.get("status") or "Pending"
        company["phone"] = company.get("contact") or company.get("hr_phone_number") or company.get("phone")
        company["location"] = company.get("address") or ", ".join(filter(None, [company.get("city"), company.get("state")]))
        company["total_job_posts"] = total_job_posts
        company["total_applications"] = total_applications
        company["hired_students"] = hired_students
        company["pending_reviews"] = pending_reviews
        company["job_posts"] = job_posts

        return {"success": True, "company": company}, 200
    except Exception as e:
        print(f"[ADMIN COMPANY DETAIL ERROR] {e}")
        company["name"] = company.get("company_name") or company.get("name") or "Company"
        company["status"] = company.get("admin_status") or company.get("status") or "Pending"
        company["total_job_posts"] = 0
        company["total_applications"] = 0
        company["hired_students"] = 0
        company["pending_reviews"] = 0
        company["job_posts"] = []
        return {"success": True, "company": company}, 200
    finally:
        conn.close()


def _notify_company(client_id, title, message):
    try:
        notification_model.create_notification(
            user_type="client", user_id=client_id, title=title, message=message
        )
    except Exception as e:
        print(f"[NOTIFICATION] Failed to notify client {client_id}: {e}")


def approve_company(client_id):
    client = client_model.find_by_id(client_id)
    if not client:
        return {"success": False, "message": "Company not found."}, 404

    client_model.update_admin_status(client_id, "Approved")
    _notify_company(client_id, "Account Approved",
                     "Your company account has been approved by an administrator.")
    return {"success": True, "message": "Company approved."}, 200


def reject_company(client_id):
    client = client_model.find_by_id(client_id)
    if not client:
        return {"success": False, "message": "Company not found."}, 404

    client_model.update_admin_status(client_id, "Rejected")
    _notify_company(client_id, "Account Rejected",
                     "Your company account application was rejected by an administrator.")
    return {"success": True, "message": "Company rejected."}, 200


def block_company(client_id):
    client = client_model.find_by_id(client_id)
    if not client:
        return {"success": False, "message": "Company not found."}, 404

    client_model.update_admin_status(client_id, "Blocked")
    _notify_company(client_id, "Account Blocked",
                     "Your company account has been blocked by an administrator. Contact support for help.")
    return {"success": True, "message": "Company blocked."}, 200


def delete_company_account(client_id):
    client = client_model.find_by_id(client_id)
    if not client:
        return {"success": False, "message": "Company not found."}, 404

    client_model.delete_client(client_id)
    return {"success": True, "message": "Company account deleted."}, 200
