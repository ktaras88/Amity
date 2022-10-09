from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings

from .models import Profile


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    profile_id = serializers.IntegerField(default=None)

    def validate(self, attrs):
        data = super(TokenObtainPairSerializer, self).validate(attrs)

        if attrs['profile_id']:
            profile = Profile.objects.filter(id=attrs['profile_id'], user_id=self.user.id).first()
            if not profile:
                raise ValidationError('Test')
        else:
            profile = self.user.profile_set.first()

        refresh = self.get_token(self.user, profile=profile)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data

    @classmethod
    def get_token(cls, user, **kwargs):
        token = super().get_token(user)
        token['profile_id'] = kwargs['profile'].id
        token['role'] = kwargs['profile'].role

        return token
