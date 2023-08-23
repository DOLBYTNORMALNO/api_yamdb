from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение на чтение для всех, но на запись только для администратора.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'admin'


class IsAdmin(permissions.BasePermission):
    """
    Разрешение только для администратора или суперпользователя.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser)


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Разрешение на доступ к данным своей учетной записи или если пользователь - администратор.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.role == 'admin'


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Разрешение на чтение для всех, но на запись только для аутентифицированных пользователей.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    """
    Разрешение на редактирование и удаление только для автора, модератора или администратора.
    """

    def has_object_permission(self, request, view, obj):
        return (
                obj.author == request.user or
                request.user.role in ['moderator', 'admin']
        )
