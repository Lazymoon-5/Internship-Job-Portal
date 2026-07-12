"""
Notifications controller — for the Admin's own notifications page.
(Same notification system is reusable for Student/Client too, since
models/notification.py takes user_type as a parameter.)
"""

import models.notification as notification_model


def get_notifications(admin_id, args):
    page = int(args.get("page", 1))
    per_page = int(args.get("per_page", 20))

    notifications, total = notification_model.list_notifications("admin", admin_id, page, per_page)
    unread_count = notification_model.count_unread("admin", admin_id)

    return {
        "success": True,
        "notifications": notifications,
        "total": total,
        "unread_count": unread_count,
    }, 200


def mark_all_notifications_read(admin_id):
    notification_model.mark_all_read("admin", admin_id)
    return {"success": True, "message": "All notifications marked as read."}, 200


def mark_notification_read(notification_id):
    updated = notification_model.mark_one_read(notification_id)
    if not updated:
        return {"success": False, "message": "Notification not found."}, 404
    return {"success": True, "message": "Notification marked as read."}, 200
