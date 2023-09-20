from rest_framework import permissions


class OwnerOrAdminOrReadOnly(permissions.BasePermission):
    """Is owner or read only."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user or bool(
            request.user and request.user.is_staff)


class OwnerOrAdminPermission(permissions.BasePermission):
    """Only for owner."""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or bool(
            request.user and request.user.is_staff)
