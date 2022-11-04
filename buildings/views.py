from django.db.models import Value, CharField
from django.db.models.functions import Concat
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from amity_api.permission import IsAmityAdministratorOrSupervisor
from .models import Building
from .serializers import CreateBuildingSerializer, ListBuildingSerializer


class BuildingViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    permission_classes = (IsAmityAdministratorOrSupervisor,)
    queryset = Building.objects.all()

    def get_queryset(self):
        pk = self.kwargs['pk']
        if self.action == 'list':
            self.queryset = Building.objects.filter(community=pk).annotate(contact_person_name=
                                                                      Concat('contact_person__first_name', Value(' '),
                                                                             'contact_person__last_name',
                                                                             output_field=CharField()))
        return self.queryset

    def get_serializer_class(self):
        if self.action == 'list':
            serializer_class = ListBuildingSerializer
        else:
            serializer_class = CreateBuildingSerializer
        return serializer_class
