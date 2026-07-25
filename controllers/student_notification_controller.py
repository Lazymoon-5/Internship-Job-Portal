"""
Notifications controller — for the Student's own notifications.
Mirrors admin/client notification controllers, for user_type='student'.
"""

import models.notification as notification_model


def get_notifications(student_id, args):
    page = int(args.get("page", 1))
    per_page = int(args.get("per_page", 20))

    notifications, total = notification_model.list_notifications("student", student_id, page, per_page)
    unread_count = notification_model.count_unread("student", student_id)

    return {
        "success": True,
        "notifications": notifications,
        "total": total,
        "unread_count": unread_count,
    }, 200


def mark_all_notifications_read(student_id):
    notification_model.mark_all_read("student", student_id)
    return {"success": True, "message": "All notifications marked as read."}, 200


def mark_notification_read(notification_id):
    updated = notification_model.mark_one_read(notification_id)
    if not updated:
        return {"success": False, "message": "Notification not found."}, 404
    return {"success": True, "message": "Notification marked as read."}, 200
