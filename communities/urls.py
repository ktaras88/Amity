from django.urls import path

from .views import CommunitiesListAPIView, ListForSearchAPIView

app_name = 'communities'

urlpatterns = [
    path('', CommunitiesListAPIView.as_view(), name='communities-list'),
    path('search-list/', ListForSearchAPIView.as_view(), name='search-list'),
]
