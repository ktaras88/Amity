from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated

from users.choices_types import ProfileRoles
from users.models import Profile


class IsOwnerNotForResident(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        perm = super().has_permission(request, view)
        role_exist = Profile.objects.filter(user=request.user).exclude(role=ProfileRoles.RESIDENT).exists()
        return bool(obj == request.user and role_exist and perm)


class IsAmityAdministrator(IsAuthenticated):
    def has_permission(self, request, view):
        perm = super().has_permission(request, view)
        return bool(perm and request.auth['role'] == ProfileRoles.AMITY_ADMINISTRATOR)
