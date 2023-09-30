from rest_framework import permissions


class OwnerOrAdminPermission(permissions.BasePermission):
    """Only for the owner of the object."""
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or bool(
            request.user and request.user.is_superuser)


class OwnerPermission(permissions.BasePermission):
    """Only author of the object."""
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view,  obj):
        return obj.author == request.user


class IsAuthorOrAdminPermission(permissions.BasePermission):
    """Only the author or admin."""
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.is_author
                or request.user.is_superuser)


class CurrentUserOrReadOnlyOrAdmin(permissions.IsAuthenticated):
    """Only the current user or read only or admin."""
    def has_object_permission(self, request, view, obj):
        user = request.user
        return (user.is_superuser
                or obj.pk == user.pk
                or request.method == 'GET'
                )
