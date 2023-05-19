from rest_framework.permissions import BasePermission


class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_industry


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_industry
