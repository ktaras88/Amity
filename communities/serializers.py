from django.contrib.auth import get_user_model
from localflavor.us.us_states import US_STATES
from rest_framework import serializers

from users.choices_types import ProfileRoles
from users.validators import phone_regex
from .models import Community, RecentActivity

User = get_user_model()


class CommunitiesListSerializer(serializers.ModelSerializer):
    contact_person_name = serializers.CharField()
    state = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = ['id', 'name', 'state', 'address', 'contact_person_name', 'phone_number', 'safety_status']

    def get_state(self, obj):
        return dict(US_STATES)[obj.state]


class CommunitySerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=[phone_regex])

    class Meta:
        model = Community
        fields = '__all__'


class CommunityEditSerializer(CommunitySerializer):
    class Meta(CommunitySerializer.Meta):
        fields = ['name', 'state', 'address', 'phone_number', 'contact_person', 'description', 'logo', 'logo_coord']


class CommunityViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = ['name', 'state', 'description', 'logo', 'logo_coord', 'safety_status']


class CommunityLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = ['logo', 'logo_coord']


class RecentActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecentActivity
        fields = '__all__'


class CommunityMembersListSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    full_name = serializers.CharField()
    building_name = serializers.CharField()

    class Meta:
        model = User
        fields = ['id', 'avatar', 'avatar_coord', 'role', 'phone_number', 'full_name', 'building_name', 'is_active']

    def get_role(self, obj):
        return dict(ProfileRoles.CHOICES)[obj['role_id']]
