from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from users.models import Profile

User = get_user_model()

admin.site.register(User)
admin.site.register(Profile)
admin.site.unregister(Group)
