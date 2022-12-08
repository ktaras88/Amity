from django.contrib.auth import get_user_model
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Value, CharField, F, Q, Case, When
from django.db.models.functions import Concat
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from localflavor.us.us_states import US_STATES
from rest_framework import mixins, generics, status
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.views import APIView

from amity_api.permission import IsAmityAdministrator, IsAmityAdministratorOrSupervisor, \
    IsAmityAdministratorOrCommunityContactPerson, IsAmityAdministratorOrSupervisorOrCoordinator
from buildings.models import Building
from users.choices_types import ProfileRoles
from users.filters import CommunityMembersFilter
from users.mixins import PropertyMixin, BelowRolesListMixin
from .models import Community, RecentActivity
from .serializers import CommunitiesListSerializer, CommunitySerializer, \
    CommunityViewSerializer, CommunityLogoSerializer, CommunityEditSerializer, RecentActivitySerializer, \
    CommunityMembersListSerializer, DetailMemberPageAccessSerializer, CommunityMemberSerializer

User = get_user_model()


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="List of communities"
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Create community"
))
class CommunitiesViewSet(mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         GenericViewSet):
    default_queryset = Community.objects.select_related('contact_person').all()
    serializer_classes = {
        'list': CommunitiesListSerializer
    }
    default_serializer_class = CommunitySerializer
    permission_classes = (IsAmityAdministratorOrSupervisor,)

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['safety_status']
    ordering_fields = ['name', 'address', 'state', 'contact_person_name']
    ordering = ['name', 'address', 'state', 'contact_person_name']
    search_fields = ['name', 'state', 'contact_person_name']

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def get_queryset(self):
        if self.action == 'list':
            query = Community.objects.annotate(contact_person_name=Concat('contact_person__first_name', Value(' '),
                                                                          'contact_person__last_name',
                                                                          output_field=CharField()))
            return query.filter(contact_person=self.request.user) if \
                self.request.auth['role'] == ProfileRoles.SUPERVISOR else query.all()
        return self.default_queryset


@method_decorator(name='put', decorator=swagger_auto_schema(
    operation_summary="Change community data"
))
@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="View community data"
))
class CommunityAPIView(generics.RetrieveUpdateAPIView):
    queryset = Community.objects.select_related('contact_person').all()
    serializer_class = CommunityViewSerializer
    permission_classes = (IsAmityAdministratorOrCommunityContactPerson,)
    http_method_names = ["put", "get"]

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return CommunityEditSerializer
        return super().get_serializer_class()


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="Search prediction for front end"
))
class SearchPredictionsAPIView(APIView):
    permission_classes = (IsAmityAdministrator,)

    def get(self, request, *args, **kwargs):
        data_for_search = Community.objects.values('name', 'state'). \
            annotate(contact_person=Concat('contact_person__first_name', Value(' '), 'contact_person__last_name')). \
            aggregate(contact_persons=ArrayAgg('contact_person', distinct=True),
                      community_names=ArrayAgg('name', distinct=True),
                      states=ArrayAgg('state', distinct=True))
        search_list = set(data_for_search['contact_persons'])
        search_list.update(data_for_search['community_names'])
        search_list.update(data_for_search['states'])
        return Response({'search_list': search_list})


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="Supervisor data for front end"
))
class SupervisorDataAPIView(APIView):
    permission_classes = (IsAmityAdministratorOrSupervisor,)

    def get(self, request, *args, **kwargs):
        supervisor_data = User.objects.values('email', 'phone_number').\
            filter(profile__role=ProfileRoles.SUPERVISOR). \
            annotate(supervisor_name=Concat('first_name', Value(' '), 'last_name'), supervisor_id=F('id'))

        return Response({'supervisor_data': list(supervisor_data)})


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="List of states for frontend"
))
class StatesListAPIView(APIView):
    permission_classes = (IsAmityAdministratorOrSupervisor,)

    def get(self, request, *args, **kwargs):
        return Response({'states_list': dict(US_STATES)})


@method_decorator(name='put', decorator=swagger_auto_schema(
    operation_summary="Change safety lock status for community and its buildings"
))
class SwitchCommunitySafetyLockAPIView(generics.UpdateAPIView):
    queryset = Community.objects.all()
    permission_classes = (IsAmityAdministratorOrCommunityContactPerson,)
    http_method_names = ["put"]

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.switch_safety_status()
        instance.create_recent_activity_record(user_id=self.request.user.id, activity=RecentActivity.SAFETY_STATUS)
        return Response({'safety_status': instance.safety_status}, status=status.HTTP_200_OK)


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="For devops. Return status 200"
))
class HealthAPIView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)


@method_decorator(name='put', decorator=swagger_auto_schema(
    operation_summary="Upload new community logo"
))
@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="View community logo"
))
@method_decorator(name='delete', decorator=swagger_auto_schema(
    operation_summary="Delete community logo"
))
class CommunityLogoAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunityLogoSerializer
    permission_classes = (IsAmityAdministratorOrCommunityContactPerson,)
    http_method_names = ["put", "get", "delete"]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.logo:
            instance.logo.delete()
            instance.logo_coord = None
            instance.save()
            return Response({'message': 'Community logo removed'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'There is no community logo.'}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="View community recent activity as a list"
))
class RecentActivityAPIView(generics.ListAPIView):
    permission_classes = (IsAmityAdministratorOrCommunityContactPerson,)
    serializer_class = RecentActivitySerializer

    def get_queryset(self):
        return RecentActivity.objects.filter(community=self.kwargs['pk'])[:50]


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_summary="Create new member in the community"
))
@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="View list of community members"
))
class CommunityMembersListAPIView(PropertyMixin, generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAmityAdministratorOrCommunityContactPerson, )
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = CommunityMembersFilter
    ordering_fields = ['full_name']
    ordering = ['is_active', 'full_name']
    search_fields = ['full_name']

    def get_queryset(self):
        if self.request.method == 'GET':
            pk = self.kwargs['pk']
            queryset = User.objects.filter(Q(communities__id=pk) | Q(buildings__community__id=pk)).values(
                'id', 'avatar', 'avatar_coord', 'phone_number', 'is_active').annotate(
                full_name=Concat('first_name', Value(' '), 'last_name', output_field=CharField()),
                role_id=Case(
                    When(buildings__id__isnull=True, then=Value(ProfileRoles.SUPERVISOR)),
                    default=Value(ProfileRoles.COORDINATOR),
                    output_field=CharField(),
                ),
                building_name=Case(
                    When(buildings__id__isnull=True, then=Value('Managing all buildings')),
                    default=F('buildings__name'),
                    output_field=CharField(),
                ),
            )
            return queryset
        return super().get_queryset()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CommunityMembersListSerializer
        return CommunityMemberSerializer

    def perform_create(self, serializer):
        user_data = dict(serializer.validated_data)
        property_id = user_data['property']
        del user_data['property']
        user = User.objects.create_user(**user_data)
        if model := self.get_property_model_by_role(user_data['role']):
            model.objects.filter(id=property_id).update(contact_person=user)


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="Members search prediction for front end"
))
class MembersSearchPredictionsAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        data_for_search = User.objects.filter(Q(communities__id=pk) | Q(buildings__community__id=pk)).\
            annotate(full_name=Concat('first_name', Value(' '), 'last_name')). \
            aggregate(full_names=ArrayAgg('full_name', distinct=True))
        return Response({'members_search_list': data_for_search['full_names']}, status=status.HTTP_200_OK)


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="Buildings search prediction for frontend"
))
class BuildingsNameListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        list_of_buildings = Building.objects.filter(community__id=pk).values_list('name', flat=True).distinct()
        return Response({'buildings_search_list': list_of_buildings}, status=status.HTTP_200_OK)


class DetailMemberPageAPIView(APIView):
    permission_classes = (IsAmityAdministratorOrSupervisor,)

    def get(self, request, pk, member_pk, *args, **kwargs):
        if not Community.objects.filter(id=pk).exists():
            return Response({'error': "There is no such community"}, status=status.HTTP_400_BAD_REQUEST)
        if member := User.objects.filter(id=member_pk).\
                values('email', 'phone_number', 'avatar', 'avatar_coord', 'profile__role').\
                annotate(full_name=Concat('first_name', Value(' '), 'last_name')):
            return Response({'member_data': member}, status=status.HTTP_200_OK)
        return Response({'error': 'There is no such user.'}, status=status.HTTP_400_BAD_REQUEST)


class DetailMemberPageAccessListAPIView(generics.ListAPIView):
    permission_classes = (IsAmityAdministratorOrSupervisor,)
    serializer_class = DetailMemberPageAccessSerializer

    def get_queryset(self):
        member_pk = self.kwargs['member_pk']
        query = Building.objects.filter(Q(contact_person=member_pk) | Q(community__contact_person=member_pk)).\
            values('name', 'address', 'phone_number')
        return query

    def list(self, request, pk, member_pk,  *args, **kwargs):
        if not Community.objects.filter(id=pk).exists():
            return Response({'error': "There is no such community"}, status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(id=member_pk).exists():
            return Response({'error': 'There is no such user.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)


class InactivateSpecificMemberAPIView(APIView):
    permission_classes = (IsAmityAdministratorOrSupervisorOrCoordinator,)

    def put(self, request, *args, **kwargs):
        if not Community.objects.filter(id=kwargs['pk']).exists():
            return Response({'error': "There is no such community"}, status=status.HTTP_400_BAD_REQUEST)
        if user := User.objects.filter(id=kwargs['member_pk']).first():
            user.inactivate_user()
            user.communities.update(contact_person=None)
            user.buildings.update(contact_person=None)
            return Response({'is_active': user.is_active}, status=status.HTTP_200_OK)
        return Response({'error': 'There is no such user.'}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="List of free roles in community below the auth user's role"
))
class BelowRolesWithFreePropertiesListAPIView(BelowRolesListMixin, APIView):
    permission_classes = (IsAmityAdministratorOrCommunityContactPerson, )

    @staticmethod
    def property_list(model, filter_name):
        return model.objects.values('id', 'name').filter(**filter_name, contact_person__isnull=True)

    def get(self, request, pk, *args, **kwargs):
        roles_list = self.get_roles_list(request)
        for role in roles_list[:]:
            if role['id'] == ProfileRoles.SUPERVISOR:
                property_list = self.property_list(Community, {'pk': pk})
                role['property_list'] = property_list if property_list else roles_list.remove(role)

            elif role['id'] == ProfileRoles.COORDINATOR:
                property_list = self.property_list(Building, {'community_id': pk})
                role['property_list'] = property_list if property_list else roles_list.remove(role)

        return Response({'roles_list': roles_list}, status=status.HTTP_200_OK)


@method_decorator(name='put', decorator=swagger_auto_schema(
    operation_summary="Unassign member from specific community"
))
class CommunityUnassignContactPersonAPIView(APIView):
    permission_classes = (IsAmityAdministratorOrCommunityContactPerson, )

    def put(self, request, pk, *args, **kwargs):
        Community.objects.filter(id=pk).update(contact_person=None)
        return Response(status=status.HTTP_200_OK)
