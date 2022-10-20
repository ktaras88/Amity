from rest_framework import serializers

from .models import Community


class CommunitiesListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Community
        fields = ['name', 'state', 'address', 'contact_person', 'phone_number', 'safety_status']

    contact_person = serializers.SerializerMethodField('get_contact_person_name')

    def get_contact_person_name(self, obj):
        return str(obj.contact_person)
