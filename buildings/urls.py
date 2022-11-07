from django.urls import path

from .views import BuildingViewSet

app_name = 'buildings'

urlpatterns = [
  path('communities/<int:pk>/buildings/', BuildingViewSet.as_view({'post': 'create', 'get': 'list'}), name='buildings-list'),
]
