from rest_framework import permissions


class OwnerOrReadOnlyPermission(permissions.BasePermission):
    """Is owner or read only."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class OwnerOrAdminPermission(permissions.BasePermission):
    """Only for owner."""
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or bool(
            request.user and request.user.is_superuser)


class OwnerPermission(permissions.BasePermission):
    """Only author."""
    def has_object_permission(self, request, view,  obj):
        return obj.author == request.user


class IsAuthorOrAdminPermission(permissions.BasePermission):
    """Only author and admin can post images."""
    def has_permission(self, request, view):
        return request.user.author or request.user.is_superuser
