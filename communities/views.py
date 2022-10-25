from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import GenericViewSet

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
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   GenericViewSet):

    queryset = Community.objects.select_related('contact_person').all()
    serializer_class = CommunitySerializer
    permission_classes = (IsAmityAdministratorOrSupervisor, )
