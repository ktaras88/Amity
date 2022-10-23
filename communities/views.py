from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter

from amity_api.permission import IsAmityAdministrator
from .models import Community
from .serializers import CommunitiesListSerializer


class CommunitiesListAPIPagination(PageNumberPagination):
    page_size_query_param = 'size'


class CommunitiesListAPIView(ListAPIView):
    serializer_class = CommunitiesListSerializer
    permission_classes = (IsAmityAdministrator, )
    pagination_class = CommunitiesListAPIPagination

    filter_backends = [OrderingFilter]
    ordering = ['-safety_status', 'name', 'state']

    def get_queryset(self):
        queryset = Community.objects.select_related('contact_person').all()
        safety_on = str(self.request.query_params.get('safety_on')).lower()
        safety_off = str(self.request.query_params.get('safety_off')).lower()

        if safety_on == 'true':
            return queryset.filter(safety_status=True) if safety_off != 'true' else queryset
        return queryset.filter(safety_status=False) if safety_off == 'true' else queryset
