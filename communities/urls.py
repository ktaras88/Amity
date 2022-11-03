from django.urls import path

from .views import SearchPredictionsAPIView, SupervisorDataAPIView, \
    StatesListAPIView, SwitchSafetyLockAPIView, CommunitiesViewSet

app_name = 'communities'

urlpatterns = [
    path('', CommunitiesViewSet.as_view({'post': 'create', 'get': 'list'}), name='communities-list'),
    path('search-predictions/', SearchPredictionsAPIView.as_view(), name='search-predictions'),
    path('supervisor-data/', SupervisorDataAPIView.as_view(), name='supervisor-data'),
    path('states/', StatesListAPIView.as_view(), name='states-list'),
    path('<int:pk>/switch-safety-status/', SwitchSafetyLockAPIView.as_view(), name='switch-safety-status'),
]
