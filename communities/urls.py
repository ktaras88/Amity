from django.urls import path

from .views import CommunitiesListAPIView, CommunityViewSet, SearchPredictionsAPIView, SupervisorDataAPIView, \
    StatesListAPIView

app_name = 'communities'

urlpatterns = [
    path('', CommunitiesListAPIView.as_view(), name='communities-list'),
    path('', CommunityViewSet.as_view({'post': 'create'}), name='community-create'),
    path('search-predictions/', SearchPredictionsAPIView.as_view(), name='search-predictions'),
    path('supervisor-data/', SupervisorDataAPIView.as_view(), name='supervisor-data'),
    path('states/', StatesListAPIView.as_view(), name='states-list'),
]
