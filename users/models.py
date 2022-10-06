from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.db import models


class User(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField('first name', max_length=100, null=True, blank=True)
    last_name = models.CharField('last name', max_length=100, null=True, blank=True)
    email = models.EmailField('email address', unique=True)
    phone_number = models.CharField('phone number', max_length=20, null=True, blank=True)
    password = models.CharField('password', max_length=100, null=True, blank=True)
    avatar = models.ImageField('user avatar', null=True, blank=True, upload_to='/')
    avatar_coord = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


class Profile(models.Model):
    AMITY_ADMINISTRATOR = 1
    SUPERVISOR = 2
    COORDINATOR = 3
    OBSERVER = 4
    RESIDENT = 5

    ROLE_CHOICES = (
        (AMITY_ADMINISTRATOR, 'Amity administrator'),
        (SUPERVISOR, 'supervisor'),
        (COORDINATOR, 'coordinator'),
        (OBSERVER, 'observer'),
        (RESIDENT, 'resident'),
    )

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.SmallIntegerField(choices=ROLE_CHOICES)
