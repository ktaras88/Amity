from django.contrib.auth import get_user_model
from localflavor.us.us_states import US_STATES
from rest_framework import serializers

from .models import Community
User = get_user_model()


class CommunitiesListSerializer(serializers.ModelSerializer):
    state = serializers.SerializerMethodField()
    contact_person = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = ['id', 'name', 'state', 'address', 'contact_person', 'phone_number', 'safety_status']

    def get_contact_person(self, obj):
        return obj.contact_person.get_full_name() if obj.contact_person else ''

    def get_state(self, obj):
        return dict(US_STATES)[obj.state] if obj.contact_person else ''


class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = '__all__'
