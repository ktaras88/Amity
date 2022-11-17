from django_filters import rest_framework as filters, CharFilter


class CustomFilterSetForBuildingsAndRoles(filters.FilterSet):
    role_id_search = CharFilter(method='get_users_by_role_id_iexact')
    building_name_search = CharFilter(method='get_users_by_building_name_iexact')

    @staticmethod
    def get_users_by_role_id_iexact(queryset, name, value):
        return queryset.filter(role_id=value)

    @staticmethod
    def get_users_by_building_name_iexact(queryset, name, value):
        return queryset.filter(building_name__icontains=value)
