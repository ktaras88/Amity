from django.db.models import Value, CharField
from django.db.models.functions import Concat
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView

from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter, SearchFilter

from amity_api.permission import IsAmityAdministrator
from .models import Community
from .serializers import CommunitiesListSerializer


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
    search_fields = ['name', 'state', 'contact_person__first_name', 'contact_person__last_name']
