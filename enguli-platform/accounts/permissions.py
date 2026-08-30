from rest_framework import permissions


class IsAdminOrFieldEngineer(permissions.BasePermission):
    """
    Grants read access to authenticated users, but write access
    exclusively to ADMIN, FIELD_ENGINEER, and superusers.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        user_role = getattr(getattr(request.user, 'profile', None), 'role', 'OBSERVER')
        return user_role in ['ADMIN', 'FIELD_ENGINEER'] or request.user.is_superuser