from rest_framework.generics import ListAPIView

from amity_api.permission import IsAmityAdministrator
from .models import Community
from .serializers import CommunitiesListSerializer


class CommunitiesListAPIView(ListAPIView):
    queryset = Community.objects.select_related('contact_person').all()
    serializer_class = CommunitiesListSerializer
    permission_classes = (IsAmityAdministrator, )
