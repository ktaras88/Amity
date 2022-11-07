from localflavor.us.us_states import US_STATES
from rest_framework import serializers

from communities.models import Community
from .models import Building


class CreateBuildingSerializer(serializers.ModelSerializer):
    community_id = serializers.IntegerField()

    class Meta:
        model = Building
        fields = ['community_id', 'name', 'state', 'address', 'contact_person', 'phone_number', 'safety_status']

    def validate(self, attr):
        if not Community.objects.filter(id=attr['community_id']).exists():
            raise serializers.ValidationError({'error': "There is no such community"})
        return attr


class ListBuildingSerializer(serializers.ModelSerializer):
    contact_person_name = serializers.CharField()
    state = serializers.SerializerMethodField()

    class Meta:
        model = Building
        fields = ['id', 'community', 'name', 'state', 'address', 'contact_person_name', 'phone_number', 'safety_status']

    def get_state(self, obj):
        return dict(US_STATES)[obj.state]
