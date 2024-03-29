from rest_framework import permissions


class IsAdminUserOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """ Класс доступа. Админ или только чтение. """

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and request.user.is_active
                and request.user.is_staff)


class IsOwnerOrIsAdminOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """ Класс доступа. Админ, автор или только чтение. """

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and request.user.is_active
                and obj.author == request.user
                or request.user.is_staff)
