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
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.views import APIView

from amity_api.permission import IsAmityAdministrator, IsAmityAdministratorOrSupervisor, \
    IsAmityAdministratorOrCommunityContactPerson
from users.choices_types import ProfileRoles
from .models import Community, RecentActivity
from .serializers import CommunitiesListSerializer, CommunitySerializer, \
    CommunityViewSerializer, CommunityLogoSerializer, CommunityEditSerializer, RecentActivitySerializer, \
    CommunityMembersListSerializer

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
            annotate(contact_person=Concat('contact_person__first_name', Value('  '), 'contact_person__last_name')). \
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
        supervisor_data = User.objects.values('email', 'phone_number'). \
            annotate(supervisor_name=Concat('first_name', Value('  '), 'last_name'))

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


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="View list of community members"
))
class CommunityMembersListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAmityAdministratorOrCommunityContactPerson, )
    serializer_class = CommunityMembersListSerializer

    def get_queryset(self):
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
