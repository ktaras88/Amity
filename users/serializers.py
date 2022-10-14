from django.contrib.auth.models import update_last_login

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as SimpleJWTTokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings

from .models import InvitationToken, Profile, User


class TokenObtainPairSerializer(SimpleJWTTokenObtainPairSerializer):
    profile_id = serializers.IntegerField(default=None)

    def validate(self, attrs):
        data = super(SimpleJWTTokenObtainPairSerializer, self).validate(attrs)

        if attrs['profile_id']:
            profile = Profile.objects.filter(id=attrs['profile_id'], user_id=self.user.id).first()
            if not profile:
                raise ValidationError('There is no profile')
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


class RequestEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ["email"]


class SecurityCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)
    security_code = serializers.CharField(min_length=6, max_length=6)

    class Meta:
        fields = ["email", "security_code"]


class CreateNewPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(min_length=2, write_only=True, required=True)
    confirm_password = serializers.CharField(min_length=2, write_only=True, required=True)

    class Meta:
        fields = ['password', 'confirm_password']

    def validate(self, attr):
        if attr['password'] != attr['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        user_id = InvitationToken.objects.get(key=str(attr['token'])).user_id
        if user := User.objects.filter(id=user_id).first():
            attr['user'] = user
        else:
            raise serializers.ValidationError("There is no account with that email.")
        return attr
