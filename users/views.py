from django.contrib.auth import get_user_model
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Value, Subquery, F
from django.db.models.functions import Concat, Coalesce
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView as SimpleJWTTokenObtainPairView

from buildings.models import Building
from communities.models import Community
from .filters import CommunityMembersFilter

from amity_api.permission import IsOwnerNotForResident, IsAmityAdministratorOrSupervisorOrCoordinator, \
    IsAmityAdministratorOrSupervisor
from .models import InvitationToken
from .serializers import RequestEmailSerializer, SecurityCodeSerializer, TokenObtainPairSerializer, \
    CreateNewPasswordSerializer, UserAvatarSerializer, UserProfileInformationSerializer,\
    UserPasswordInformationSerializer, MemberSerializer, MembersListSerializer
from .mixins import PropertyMixin, RoleMixin, BelowRolesListMixin

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
    operation_summary="Retrieve user profile information"
))
@method_decorator(name='put', decorator=swagger_auto_schema(
    operation_summary="Change user profile information"
))
class UserProfileInformationAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileInformationSerializer
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
class UsersRoleListAPIView(RoleMixin, APIView):
    permission_classes = (IsAmityAdministratorOrSupervisorOrCoordinator, )

    def get(self, request, role, *args, **kwargs):
        if role_id := self.get_role_id(role):
            users_role_list = User.objects.filter(profile__role=role_id).values('id'). \
                annotate(full_name=Concat('first_name', Value(' '), 'last_name'))
            return Response({'data': list(users_role_list)})
        else:
            return Response({'error': 'Role does not exists'}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="Get authenticated user id"
))
class GetAuthenticatedUserIdAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        return Response({'user_id': request.user.id}, status=status.HTTP_200_OK)


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="Get all the members in system"
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Create new member"
))
class MembersAPIView(PropertyMixin, generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAmityAdministratorOrSupervisorOrCoordinator, )
    serializer_class = MemberSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = CommunityMembersFilter
    filterset_fields = ['full_name']
    ordering_fields = ['full_name']
    ordering = ['-is_active', 'full_name']
    search_fields = ['full_name']

    def get_queryset(self):
        if self.request.method == 'GET':
            query = User.objects.values('avatar', 'avatar_coord', 'email', 'phone_number').\
                annotate(full_name=Concat('first_name', Value(' '), 'last_name'), role=F('profile__role'),
                         communities_list=ArrayAgg('communities__name', distinct=True),
                         buildings_list=ArrayAgg('buildings__name', distinct=True))
            return query
        else:
            return super().get_queryset()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MembersListSerializer
        return MemberSerializer

    def perform_create(self, serializer):
        user = User.objects.create_user(**serializer.validated_data)
        if property_id := self.request.POST.get('property'):
            if model := self.get_property_model_by_role(serializer.validated_data['role']):
                model.objects.filter(id=property_id).update(contact_person=user)


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="Property list by role"
))
class PropertiesWithoutContactPersonAPIView(RoleMixin, PropertyMixin, APIView):
    permission_classes = (IsAmityAdministratorOrSupervisorOrCoordinator, )

    def get(self, request, role, *args, **kwargs):
        if role_id := self.get_role_id(role):
            if model := self.get_property_model_by_role(role_id):
                properties = model.objects.filter(contact_person_id__isnull=True).values('id', 'name')
                return Response({'data': list(properties)}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Property does not exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Role does not exists'}, status=status.HTTP_400_BAD_REQUEST)


class ActivateSpecificMemberAPIView(APIView):
    permission_classes = (IsAmityAdministratorOrSupervisorOrCoordinator, )

    def put(self, request, *args, **kwargs):
        if user := User.objects.filter(id=kwargs['pk']).first():
            user.activate_user()
            return Response({'is_active': user.is_active}, status=status.HTTP_200_OK)
        return Response({'error': 'There is no such user.'}, status=status.HTTP_400_BAD_REQUEST)


class InactivateSpecificMemberAPIView(APIView):
    permission_classes = (IsAmityAdministratorOrSupervisor,)

    def put(self, request, *args, **kwargs):
        if user := User.objects.filter(id=kwargs['pk']).first():
            user.inactivate_user()
            user.communities.update(contact_person=None)
            user.buildings.update(contact_person=None)
            return Response({'is_active': user.is_active}, status=status.HTTP_200_OK)
        return Response({'error': 'There is no such user.'}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="List of roles below the auth user's role"
))
class BelowRolesListAPIView(BelowRolesListMixin, APIView):
    permission_classes = (IsAmityAdministratorOrSupervisorOrCoordinator, )

    def get(self, request, *args, **kwargs):
        roles_list = self.get_roles_list(request)
        return Response({'roles_list': roles_list}, status=status.HTTP_200_OK)

