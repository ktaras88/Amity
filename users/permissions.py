import jwt

from decouple import config
from rest_framework import permissions

from .models import User


class IsAccessToken(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        token = request.GET.get('token')
        user_id = jwt.decode(token, config('SECRET_KEY'), algorithms=["HS256"])['user_id']
        return bool(User.objects.filter(id=user_id).exists())
