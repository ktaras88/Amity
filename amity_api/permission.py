from rest_framework import permissions, status
from rest_framework.response import Response

from users.choices_types import ProfileRoles
from users.models import Profile


class IsOwnerOrReadOnlyNotForResident(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if obj == request.user:
            roles_count = Profile.objects.filter(user=request.user).exclude(role=ProfileRoles.RESIDENT).count()
            return True if roles_count > 0 else Response({'error': 'Not for resident'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'error': 'You are not owner this profile'}, status=status.HTTP_403_FORBIDDEN)
