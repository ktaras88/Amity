import profile

from django.contrib.auth import authenticate, get_user_model
from django.core import exceptions
import django.contrib.auth.password_validation as validators

from django.contrib.auth.models import update_last_login

from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError, AuthenticationFailed as DRFAuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as SimpleJWTTokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings

from .choices_types import ProfileRoles
from .models import InvitationToken, Profile

User = get_user_model()


class AuthenticationFailed(DRFAuthenticationFailed):
    status_code = status.HTTP_400_BAD_REQUEST


class TokenObtainPairSerializer(SimpleJWTTokenObtainPairSerializer):
    profile_id = serializers.IntegerField(default=None)

    def _pre_validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            "password": attrs["password"],
        }
        try:
            authenticate_kwargs["request"] = self.context["request"]
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            raise AuthenticationFailed(
                self.error_messages["no_active_account"],
                "no_active_account",
            )

        return {}

    def validate(self, attrs):
        data = self._pre_validate(attrs)

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
    token = serializers.CharField(required=True)
    password = serializers.CharField(min_length=2, write_only=True, required=True)
    confirm_password = serializers.CharField(min_length=2, write_only=True, required=True)

    class Meta:
        fields = ['password', 'confirm_password']

    def validate(self, attr):
        if attr['password'] != attr['confirm_password']:
            raise serializers.ValidationError({'error': "Passwords do not match."})
        if token := InvitationToken.objects.filter(key=str(attr['token'])).first():
            attr['user'] = token.user
        else:
            raise serializers.ValidationError({'error': "Invalid token."})

        try:
            validators.validate_password(password=attr['password'])
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return attr


class UserAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['avatar', 'avatar_coord']


class UserGeneralInformationSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'role']

    def get_role(self, obj):
        role = self.context['request'].auth['role']
        return role

    def update(self, instance, validated_data):
        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']

        instance.save()

        return instance


class UserContactInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'phone_number']
        read_only_fields = ('email',)
    #
    # def validate_phone_number(self, value):
    #     user = self.context['request'].user
    #     if User.objects.exclude(pk=user.pk).filter(phone_number=value).exists():
    #         raise serializers.ValidationError({"phone_number": "This phone number is already in use."})
    #     return value
    #
    # def update(self, instance, validated_data):
    #     instance.phone_number = validated_data['phone_number']
    #
    #     instance.save()
    #
    #     return instance


class UserPasswordInformationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validators.validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['old_password', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': "Password fields didn't match."})

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({'old_password': "Old password is not correct"})
        return value

    def update(self, instance, validated_data):

        instance.set_password(validated_data['password'])
        instance.save()

        return instance
