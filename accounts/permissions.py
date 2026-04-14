def is_owner_or_admin(user, obj):
    """
    Return True if the user is the object owner or an admin (is_staff).
    """
    return obj == user or user.is_staff


def is_admin_user(user):
    """
    Return True if the user is an admin (is_staff).
    """
    return user and user.is_staff
