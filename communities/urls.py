from django.urls import path


from .views import CommunitiesListAPIView, CommunityViewSet, ListForSearchAPIView, SupervisorDataAPIView

app_name = 'communities'

urlpatterns = [
    path('', CommunitiesListAPIView.as_view(), name='communities-list'),
    path('', CommunityViewSet.as_view({'post': 'create'}), name='community-create'),
    path('search-list/', ListForSearchAPIView.as_view(), name='search-list'),
    path('supervisor-data/', SupervisorDataAPIView.as_view(), name='supervisor-data'),
]
