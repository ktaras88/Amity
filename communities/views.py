from django.contrib.auth import get_user_model
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Value, CharField
from django.db.models.functions import Concat
from django_filters.rest_framework import DjangoFilterBackend
from localflavor.us.us_states import US_STATES
from rest_framework import mixins, generics
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.views import APIView

from amity_api.permission import IsAmityAdministrator, IsAmityAdministratorOrSupervisor
from .models import Community
from .serializers import CommunitiesListSerializer, CommunitySerializer, SwitchSafetyLockSerializer

User = get_user_model()


class CommunitiesListAPIPagination(PageNumberPagination):
    page_size_query_param = 'size'


class CommunitiesListAPIView(ListAPIView):
    queryset = Community.objects.annotate(contact_person_name=Concat('contact_person__first_name', Value(' '),
                                                                     'contact_person__last_name',
                                                                     output_field=CharField())).all()
    serializer_class = CommunitiesListSerializer
    permission_classes = (IsAmityAdministrator, )
    pagination_class = CommunitiesListAPIPagination

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['safety_status']
    ordering_fields = ['name', 'address', 'state', 'contact_person_name']
    ordering = ['name', 'address', 'state', 'contact_person_name']
    search_fields = ['name', 'state', 'contact_person_name']


class CommunityViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = Community.objects.select_related('contact_person').all()
    serializer_class = CommunitySerializer
    permission_classes = (IsAmityAdministratorOrSupervisor, )

    
class SearchPredictionsAPIView(APIView):
    permission_classes = (IsAmityAdministrator,)

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

    def get(self,  request, *args, **kwargs):
        supervisor_data = User.objects.values('email', 'phone_number').\
            annotate(supervisor_name=Concat('first_name', Value('  '), 'last_name'))

        return Response({'supervisor_data': list(supervisor_data)})


class StatesListAPIView(APIView):
    permission_classes = (IsAmityAdministratorOrSupervisor, )

    def get(self, request, *args, **kwargs):
        return Response({'states_list': dict(US_STATES)})


class SwitchSafetyLockAPIView(generics.UpdateAPIView):
    queryset = Community.objects.all()
    permission_classes = (IsAmityAdministratorOrSupervisor, )
    serializer_class = SwitchSafetyLockSerializer
