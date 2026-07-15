import models.client_profile as profile_model


def get_profile(client_id):
    profile = profile_model.get_profile(client_id)
    if not profile:
        return {"success": False, "message": "Company not found."}, 404
    return {"success": True, "profile": profile}, 200


def update_profile(client_id, data, mark_completed=False):
    updated = profile_model.update_profile(client_id, data)

    if mark_completed:
        profile_model.mark_profile_completed(client_id)

    if not updated and not mark_completed:
        return {"success": False, "message": "No valid fields provided to update."}, 400

    return {"success": True, "message": "Profile updated successfully."}, 200
