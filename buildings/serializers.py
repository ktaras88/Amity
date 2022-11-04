from localflavor.us.us_states import US_STATES
from rest_framework import serializers

from communities.models import Community
from .models import Building


class CreateBuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ['name', 'state', 'address', 'contact_person', 'phone_number', 'safety_status']

    def create(self, validated_data):
        community_id = self.context['view'].kwargs['pk']
        validated_data['community'] = Community.objects.filter(id=community_id).first()
        return Building.objects.create(**validated_data)


class ListBuildingSerializer(serializers.ModelSerializer):
    contact_person_name = serializers.CharField()
    state = serializers.SerializerMethodField()

    class Meta:
        model = Building
        fields = ['id', 'community', 'name', 'state', 'address', 'contact_person_name', 'phone_number', 'safety_status']

    def get_state(self, obj):
        return dict(US_STATES)[obj.state]
