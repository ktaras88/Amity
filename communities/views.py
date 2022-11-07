from django.contrib.auth import get_user_model
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Value, CharField
from django.db.models.functions import Concat
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from localflavor.us.us_states import US_STATES
from rest_framework import mixins, generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.views import APIView

from amity_api.permission import IsAmityAdministrator, IsAmityAdministratorOrSupervisor, \
    IsAmityAdministratorOrCommunityContactPerson
from users.choices_types import ProfileRoles
from .models import Community
from .serializers import CommunitiesListSerializer, CommunitySerializer, SwitchSafetyLockSerializer, \
    CommunityViewSerializer, CommunityEditSerializer

User = get_user_model()


class CommunitiesListAPIPagination(PageNumberPagination):
    page_size_query_param = 'size'


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
    permission_classes = (IsAmityAdministratorOrSupervisor, )
    pagination_class = CommunitiesListAPIPagination

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


class CommunityAPIView(generics.RetrieveUpdateAPIView):
    queryset = Community.objects.select_related('contact_person').all()
    serializer_class = CommunityViewSerializer
    permission_classes = (IsAmityAdministratorOrCommunityContactPerson, )

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return CommunityEditSerializer
        return super().get_serializer_class()


class SearchPredictionsAPIView(APIView):
    permission_classes = (IsAmityAdministrator, )

    @swagger_auto_schema(operation_summary="Search prediction for front end")
    def get(self, request, *args, **kwargs):
        data_for_search = Community.objects.values('name', 'state').\
            annotate(contact_person=Concat('contact_person__first_name', Value('  '), 'contact_person__last_name')).\
            aggregate(contact_persons=ArrayAgg('contact_person', distinct=True),
                      community_names=ArrayAgg('name', distinct=True),
                      states=ArrayAgg('state', distinct=True))
        search_list = set(data_for_search['contact_persons'])
        search_list.update(data_for_search['community_names'])
        search_list.update(data_for_search['states'])
        return Response({'search_list': search_list})


class SupervisorDataAPIView(APIView):
    permission_classes = (IsAmityAdministratorOrSupervisor, )

    @swagger_auto_schema(operation_summary="Supervisor data for front end")
    def get(self,  request, *args, **kwargs):
        supervisor_data = User.objects.values('email', 'phone_number').\
            annotate(supervisor_name=Concat('first_name', Value('  '), 'last_name'))

        return Response({'supervisor_data': list(supervisor_data)})


class StatesListAPIView(APIView):
    permission_classes = (IsAmityAdministratorOrSupervisor, )

    @swagger_auto_schema(operation_summary="List of states for frontend")
    def get(self, request, *args, **kwargs):
        return Response({'states_list': dict(US_STATES)})


@method_decorator(name='put', decorator=swagger_auto_schema(
    operation_summary="Change safety lock status"
))
class SwitchSafetyLockAPIView(generics.UpdateAPIView):
    queryset = Community.objects.all()
    permission_classes = (IsAmityAdministratorOrSupervisor, )
    serializer_class = SwitchSafetyLockSerializer
    http_method_names = ["put"]


class HealthAPIView(APIView):
    permission_classes = (AllowAny, )

    @swagger_auto_schema(operation_summary="For devops. Return status 200")
    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)
