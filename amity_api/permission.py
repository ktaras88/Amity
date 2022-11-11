from rest_framework.permissions import IsAuthenticated

from communities.models import Community
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


class IsAmityAdministratorOrSupervisor(IsAuthenticated):
    def has_permission(self, request, view):
        perm = super().has_permission(request, view)
        return bool(perm and request.auth['role'] in (ProfileRoles.AMITY_ADMINISTRATOR, ProfileRoles.SUPERVISOR))


class IsAmityAdministratorOrCommunityContactPerson(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        perm = super().has_permission(request, view)
        return bool(perm and
                    (request.auth['role'] == ProfileRoles.AMITY_ADMINISTRATOR or
                     (request.auth['role'] == ProfileRoles.SUPERVISOR and obj.contact_person.id == request.user.id)))

    def has_permission(self, request, view):
        perm = super().has_permission(request, view)
        community_contact_person_permision = Community.objects.filter(id=view.kwargs.get('pk'),
                                                                      contact_person__id=request.user.id).exists()
        return bool(perm and (request.auth['role'] == ProfileRoles.AMITY_ADMINISTRATOR or
                              (request.auth['role'] == ProfileRoles.SUPERVISOR and community_contact_person_permision)))
