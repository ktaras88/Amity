from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter

from amity_api.permission import IsAmityAdministrator
from .models import Community
from .serializers import CommunitiesListSerializer


class CommunitiesListAPIView(ListAPIView):
    queryset = Community.objects.select_related('contact_person').all()
    serializer_class = CommunitiesListSerializer
    permission_classes = (IsAmityAdministrator, )
    filter_backends = [SearchFilter]
    search_fields = ['name', 'state', 'contact_person__first_name', 'contact_person__last_name']
