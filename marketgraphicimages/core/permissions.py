from rest_framework import permissions


class OwnerOrReadOnly(permissions.BasePermission):
    """Is owner or read only."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class OwnerPermission(permissions.BasePermission):
    """Only for owner."""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
