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


def get_company_detail(client_id):
    client = client_model.find_by_id(client_id)
    if not client:
        return {"success": False, "message": "Company not found."}, 404
    return {"success": True, "company": client.to_dict()}, 200


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
