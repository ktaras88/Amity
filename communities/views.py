from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter
from amity_api.permission import IsAmityAdministrator
from .models import Community
from .serializers import CommunitiesListSerializer


class CommunitiesListAPIPagination(PageNumberPagination):
    page_size_query_param = 'size'


class CommunitiesListAPIView(ListAPIView):
    queryset = Community.objects.select_related('contact_person').all()
    serializer_class = CommunitiesListSerializer
    permission_classes = (IsAmityAdministrator, )
    pagination_class = CommunitiesListAPIPagination

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['safety_status']
    ordering = ['-safety_status', 'name', 'state']
