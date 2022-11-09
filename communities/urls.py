from django.urls import path

from .views import SearchPredictionsAPIView, SupervisorDataAPIView, \
    StatesListAPIView, SwitchCommunitySafetyLockAPIView, CommunitiesViewSet, CommunityAPIView

app_name = 'communities'

urlpatterns = [
    path('', CommunitiesViewSet.as_view({'post': 'create', 'get': 'list'}), name='communities-list'),
    path('<int:pk>/', CommunityAPIView.as_view(), name='communities-detail'),
    path('search-predictions/', SearchPredictionsAPIView.as_view(), name='search-predictions'),
    path('supervisor-data/', SupervisorDataAPIView.as_view(), name='supervisor-data'),
    path('states/', StatesListAPIView.as_view(), name='states-list'),
    path('<int:pk>/switch-safety-status/', SwitchCommunitySafetyLockAPIView.as_view(), name='switch-safety-status'),
]
