from django.urls import path

from .views import CommunitiesListAPIView, CommunityViewSet

app_name = 'communities'

urlpatterns = [
    path('', CommunitiesListAPIView.as_view(), name='communities-list'),
    path('', CommunityViewSet.as_view({'post': 'create'}), name='community-create'),
]
