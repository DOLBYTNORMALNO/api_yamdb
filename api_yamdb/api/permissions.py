from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение на чтение для всех, но на запись только для администратора.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'admin'

#class IsAmdinOrReadOnly(permissions.BasePermission):
#    def has_permission(self, request, view):
#        return (
#            request.user in permissions.SAFE_METHODS
#            or request.user.is_staff or request.user.role == 'admin'
#        )


class IsAdmin(permissions.BasePermission):
    """
    Разрешение только для администратора.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Разрешение на доступ к данным своей учетной записи или если пользователь - администратор.
    """
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.role == 'admin'
