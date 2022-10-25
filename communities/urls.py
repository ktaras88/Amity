from django.urls import path

from .views import CommunitiesListAPIView, CommunityViewSet

app_name = 'communities'

urlpatterns = [
    path('', CommunitiesListAPIView.as_view(), name='communities-list'),
    path('', CommunityViewSet.as_view({'post': 'create'}), name='community-create'),
    # path('<int:pk>/', CommunityViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='community-detail'),
]
