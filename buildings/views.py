from django.db.models import Value, CharField
from django.db.models.functions import Concat
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from amity_api.permission import IsAmityAdministratorOrSupervisor
from .models import Building
from .serializers import CreateBuildingSerializer, ListBuildingSerializer


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="List of buildings"
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Create buildings"
))
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

    def create(self, request, *args, **kwargs):
        request.data['community_id'] = self.kwargs['pk']
        return super().create(request, *args, **kwargs)
