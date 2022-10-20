from django.urls import path

from .views import CommunitiesListAPIView

app_name = 'communities'

urlpatterns = [
    path('list/', CommunitiesListAPIView.as_view(), name='communities-list'),
]
