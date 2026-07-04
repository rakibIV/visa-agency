from rest_framework.permissions import SAFE_METHODS, BasePermission


def is_authenticated_staff_user(user):
    if not getattr(user, "is_authenticated", False):
        return False

    return (
        getattr(user, "is_staff", False)
        or getattr(user, "is_superuser", False)
        or hasattr(user, "staff_profile")
    )


class IsAdminOrStaffOrReadOnly(BasePermission):
    """
    Allow public read-only access.
    Allow writes to authenticated admin or staff users.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return is_authenticated_staff_user(
            request.user,
        )


class IsAdminOrStaff(BasePermission):
    """
    Allow access only to authenticated admin or staff users.
    """

    def has_permission(self, request, view):
        return is_authenticated_staff_user(
            request.user,
        )
