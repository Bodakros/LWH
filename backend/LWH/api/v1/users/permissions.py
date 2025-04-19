# api/v1/users/permissions.py
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Дозвіл, що перевіряє чи користувач є власником складу
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_owner


class IsSeller(permissions.BasePermission):
    """
    Дозвіл, що перевіряє чи користувач є продавцем
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_seller


class IsWarehouseOwner(permissions.BasePermission):
    """
    Дозвіл для перевірки чи користувач є власником конкретного складу
    """

    def has_object_permission(self, request, view, obj):
        # Перевіряємо, чи користувач є власником конкретного складу
        return obj.owner == request.user
