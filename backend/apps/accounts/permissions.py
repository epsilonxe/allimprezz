from rest_framework.permissions import BasePermission

from libs.auth.roles import RoleManager


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and RoleManager.has_privilege(request.user.role, RoleManager.ADMIN)
        )


class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and RoleManager.has_privilege(request.user.role, RoleManager.STAFF)
        )


class IsAgent(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and RoleManager.has_privilege(request.user.role, RoleManager.AGENT)
        )
