from django.contrib.auth import get_user_model
from django.db.models import Value
from django.db.models.functions import Concat
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView as SimpleJWTTokenObtainPairView

from amity_api.permission import IsOwnerNotForResident
from .choices_types import ProfileRoles
from .models import InvitationToken
from .serializers import RequestEmailSerializer, SecurityCodeSerializer, TokenObtainPairSerializer, \
    CreateNewPasswordSerializer, UserAvatarSerializer, UserGeneralInformationSerializer, \
    UserContactInformationSerializer, UserPasswordInformationSerializer

User = get_user_model()


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_summary="Sign in. Retrieve access token."
))
class TokenObtainPairView(SimpleJWTTokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_summary="Get new security code to email"
))
class ResetPasswordRequestEmail(generics.GenericAPIView):
    serializer_class = RequestEmailSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        if user := User.objects.filter(email=email).first():
            user.send_security_code()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'There is no account with that email.'}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_summary="Confirm security code"
))
class ResetPasswordSecurityCode(generics.GenericAPIView):
    serializer_class = SecurityCodeSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if user := User.objects.filter(email=serializer.validated_data['email']).first():
            if serializer.validated_data['security_code'] == user.security_code:
                token, _ = InvitationToken.objects.get_or_create(user=user)
                return Response({'token': str(token)}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Incorrect security code. Check your secure code or request for a new one.'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'There is no user with that email.'}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_summary="Create new password"
))
class CreateNewPassword(generics.GenericAPIView):
    serializer_class = CreateNewPasswordSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user.set_password(serializer.validated_data['password'])
        user.save()
        InvitationToken.objects.filter(user_id=user.id).delete()
        return Response({'email': serializer.validated_data['email']}, status=status.HTTP_200_OK)


@method_decorator(name='put', decorator=swagger_auto_schema(
    operation_summary="Change user avatar"
))
@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="Retrieve user avatar"
))
@method_decorator(name='delete', decorator=swagger_auto_schema(
    operation_summary="Delete user avatar"
))
class UserAvatarAPIView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserAvatarSerializer
    permission_classes = (IsOwnerNotForResident, )
    http_method_names = ["put", "get", "delete"]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.avatar:
            instance.avatar.delete()
            instance.avatar_coord = None
            instance.save()
            return Response({'message': 'Avatar removed'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'There is no avatar.'}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="Retrieve user general information"
))
@method_decorator(name='put', decorator=swagger_auto_schema(
    operation_summary="Change user general information"
))
class UserGeneralInformationView(generics.RetrieveUpdateAPIView):
    serializer_class = UserGeneralInformationSerializer
    queryset = User.objects.all()
    permission_classes = (IsOwnerNotForResident,)
    http_method_names = ["put", "get"]


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="Retrieve user contact information"
))
@method_decorator(name='put', decorator=swagger_auto_schema(
    operation_summary="Change user contact information"
))
class UserContactInformationView(generics.RetrieveUpdateAPIView):
    serializer_class = UserContactInformationSerializer
    queryset = User.objects.all()
    permission_classes = (IsOwnerNotForResident,)
    http_method_names = ["put", "get"]


@method_decorator(name='put', decorator=swagger_auto_schema(
    operation_summary="Change user password"
))
class UserPasswordInformationView(generics.UpdateAPIView):
    serializer_class = UserPasswordInformationSerializer
    queryset = User.objects.all()
    permission_classes = (IsOwnerNotForResident,)
    http_method_names = ["put"]


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="Users list by role"
))
class UsersRoleListAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        role = self.kwargs['role']
        if role_id := [key for key, x in dict(ProfileRoles.CHOICES).items() if x == role]:
            users_role_list = User.objects.filter(profile__role=role_id[0]).values('id'). \
                annotate(full_name=Concat('first_name', Value(' '), 'last_name'))
            return Response({f'{role}_data': list(users_role_list)})
        else:
            return Response({'error': 'Role does not exists'}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="Get authenticated user id"
))
class GetAuthenticatedUserIdAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        return Response({'user_id': request.user.id}, status=status.HTTP_200_OK)
