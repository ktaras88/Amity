from buildings.models import Building
from communities.models import Community
from users.choices_types import ProfileRoles


class RoleMixin:
    def get_role_id(self, role):
        return next((key for key, value in dict(ProfileRoles.CHOICES).items() if value == role), None)


class PropertyMixin:
    def get_property_model_by_role(self, role_id):
        match role_id:
            case ProfileRoles.SUPERVISOR:
                return Community
            case ProfileRoles.COORDINATOR:
                return Building
        return None