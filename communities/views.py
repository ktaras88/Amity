from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Value
from django.db.models.functions import Concat
from django_filters.rest_framework import DjangoFilterBackend
from localflavor.us.us_states import US_STATES
from rest_framework import mixins
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.views import APIView

from amity_api.permission import IsAmityAdministrator, IsAmityAdministratorOrSupervisor
from .models import Community
from .serializers import CommunitiesListSerializer, CommunitySerializer


class CommunitiesListAPIPagination(PageNumberPagination):
    page_size_query_param = 'size'


class CommunitiesListAPIView(ListAPIView):
    queryset = Community.objects.select_related('contact_person').all()
    serializer_class = CommunitiesListSerializer
    permission_classes = (IsAmityAdministrator, )
    pagination_class = CommunitiesListAPIPagination

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['safety_status']
    ordering = ['name', 'address', 'state', 'contact_person__first_name', 'contact_person__last_name']
    search_fields = ['name', 'state', 'contact_person__first_name', 'contact_person__last_name']



class CommunityViewSet(mixins.CreateModelMixin,
                   GenericViewSet):

    queryset = Community.objects.select_related('contact_person').all()
    serializer_class = CommunitySerializer
    permission_classes = (IsAmityAdministratorOrSupervisor, )

    
class ListForSearchAPIView(APIView):
    permission_classes = (IsAmityAdministrator,)

    def get(self, request, *args, **kwargs):
        data_fot_search = Community.objects.values('name', 'state').\
            annotate(contact_person=Concat('contact_person__first_name', Value('  '), 'contact_person__last_name')).\
            aggregate(contact_persons=ArrayAgg('contact_person', distinct=True),
                      community_names=ArrayAgg('name', distinct=True),
                      states=ArrayAgg('state', distinct=True))
        search_list = set(data_fot_search['contact_persons'])
        search_list.update(data_fot_search['community_names'])
        search_list.update(data_fot_search['states'])
        return Response({'search_list': search_list})


class StatesListAPIView(APIView):
    permission_classes = (IsAmityAdministratorOrSupervisor, )

    def get(self, request, *args, **kwargs):
        return Response({'state_list': US_STATES})
