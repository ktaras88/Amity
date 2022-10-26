from localflavor.us.us_states import US_STATES
from rest_framework import serializers

from .models import Community


class CommunitiesListSerializer(serializers.ModelSerializer):
    contact_person_name = serializers.CharField()
    state = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = ['id', 'name', 'state', 'address', 'contact_person_name', 'phone_number', 'safety_status']

    # def get_contact_person(self, obj):
    #     return obj.contact_person.get_full_name() if obj.contact_person else ''

    def get_state(self, obj):
        return dict(US_STATES)[obj.state]
