from rest_framework.permissions import BasePermission

from core.permissions import IsAdminOrStaff as IsAdminOrReadOnly


class IsStaffOwner(BasePermission):
    """
    Allows a staff member to access only
    their own profile.
    """

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        if (
            request.user.is_authenticated
            and (
                request.user.is_staff
                or hasattr(request.user, "staff_profile")
            )
        ):
            return True

        return (
            request.user.is_authenticated
            and obj.user == request.user
        )
