from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    Allow everyone to read.
    Only admin users can create, update or delete.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return (
            request.user.is_authenticated
            and request.user.is_staff
        )


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
            and request.user.is_staff
        ):
            return True

        return (
            request.user.is_authenticated
            and obj.user == request.user
        )