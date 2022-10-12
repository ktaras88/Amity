from rest_framework import permissions


class SecurityCode(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return True
