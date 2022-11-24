from buildings.models import Building
from communities.models import Community
from users.choices_types import ProfileRoles


class RoleMixin:
    @staticmethod
    def get_role_id(role):
        return next((key for key, value in dict(ProfileRoles.CHOICES).items() if value == role), None)


class PropertyMixin:
    @staticmethod
    def get_property_model_by_role(role_id):
        match role_id:
            case ProfileRoles.SUPERVISOR:
                return Community
            case ProfileRoles.COORDINATOR:
                return Building
        return None


class BelowRolesListMixin:
    @staticmethod
    def get_roles_list(request):
        role = request.auth['role']
        roles_list = [{'id': role_key, 'name': role_name} for role_key, role_name in ProfileRoles.CHOICES
                      if role_key > role]
        return roles_list
