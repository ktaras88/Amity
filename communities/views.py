from rest_framework.generics import ListAPIView

from amity_api.permission import IsAmityAdministratorOnly
from .models import Community
from .serializers import CommunitiesListSerializer


class CommunitiesListAPIView(ListAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunitiesListSerializer
    permission_classes = (IsAmityAdministratorOnly, )
