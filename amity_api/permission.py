from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated

from users.choices_types import ProfileRoles
from users.models import Profile


class IsOwnerOrReadOnlyNotForResident(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        perm = super().has_permission(request, view)
        if request.method in permissions.SAFE_METHODS:
            return perm

        role_exist = Profile.objects.filter(user=request.user).exclude(role=ProfileRoles.RESIDENT).exists()
        return bool(obj == request.user and role_exist and perm)


class IsAmityAdministratorOnly(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        perm = super().has_permission(request, view)
        role_exist = Profile.objects.filter(user=request.user, role=ProfileRoles.AMITY_ADMINISTRATOR).exists()
        return bool(role_exist and perm)
