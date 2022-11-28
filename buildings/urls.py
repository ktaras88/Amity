from django.urls import path

from .views import BuildingViewSet, BuildingUnassignContactPersonAPIView

app_name = 'buildings'

urlpatterns = [
  path('communities/<int:pk>/buildings/', BuildingViewSet.as_view({'post': 'create', 'get': 'list'}), name='buildings-list'),
  path('communities/<int:community_id>/buildings/<int:pk>/unassign-contact-person/',
       BuildingUnassignContactPersonAPIView.as_view(), name='building-unassign-contact-person'),
]
