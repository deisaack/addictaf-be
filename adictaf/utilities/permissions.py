from rest_framework.permissions import BasePermission

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')

__all__ = ['AdictAFAdminOrReadOnly']


class AdictAFAdminOrReadOnly(BasePermission):
    """
    The request is admin user, or is a read-only request.
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_staff
        )
