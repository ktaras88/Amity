from django_filters import rest_framework as filters, CharFilter

from users.mixins import RoleMixin


class CommunityMembersFilter(filters.FilterSet):
    role_search = CharFilter(method='get_users_by_role_id_iexact')
    building_name_search = CharFilter(method='get_users_by_building_name_icontains')

    @staticmethod
    def get_users_by_role_id_iexact(queryset, name, value):
        if role_id := RoleMixin.get_role_id(name, value):
            return queryset.filter(role_id=role_id)
        else:
            return queryset.none()

    @staticmethod
    def get_users_by_building_name_icontains(queryset, name, value):
        return queryset.filter(building_name__icontains=value)
