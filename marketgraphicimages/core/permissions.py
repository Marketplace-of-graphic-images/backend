from rest_framework import permissions


class OwnerOrAdminPermission(permissions.BasePermission):
    """Only for owner."""
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or bool(
            request.user and request.user.is_superuser)


class OwnerPermission(permissions.BasePermission):
    """Only author."""
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view,  obj):
        return obj.author == request.user


class IsAuthorOrAdminPermission(permissions.BasePermission):
    """Only author and admin can post images."""
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.author or
                    request.user.is_superuser)
