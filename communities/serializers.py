from rest_framework import serializers

from .models import Community


class CommunitiesListSerializer(serializers.ModelSerializer):
    contact_person = serializers.SerializerMethodField('get_contact_person')

    class Meta:
        model = Community
        fields = ['name', 'state', 'address', 'contact_person', 'phone_number', 'safety_status']

    def get_contact_person(self, obj):
        return obj.contact_person.get_full_name()
