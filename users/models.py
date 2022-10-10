from django.contrib.auth.models import (
    AbstractBaseUser
)
from django.core.validators import RegexValidator
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser):
    phone_regex = RegexValidator(
        regex=r"^+?1?\d{10,15}$",
        message="Phone number must be entered in the format: "
                "'+999999999'. Up to 15 digits allowed.",
    )

    first_name = models.CharField('first name', max_length=100, null=True, blank=True)
    last_name = models.CharField('last name', max_length=100, null=True, blank=True)
    email = models.EmailField('email address', unique=True, db_index=True)
    phone_number = models.CharField('phone number', validators=[phone_regex], max_length=20, null=True, blank=True)
    password = models.CharField('password', max_length=100, null=True, blank=True)
    avatar = models.ImageField('user avatar', null=True, blank=True, upload_to='media/')
    avatar_coord = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    security_code = models.CharField(max_length=6, default=None, null=True, blank=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'


class Profile(models.Model):
    AMITY_ADMINISTRATOR = 1
    SUPERVISOR = 2
    COORDINATOR = 3
    OBSERVER = 4
    RESIDENT = 5

    ROLE_CHOICES = (
        (AMITY_ADMINISTRATOR, 'amity_administrator'),
        (SUPERVISOR, 'supervisor'),
        (COORDINATOR, 'coordinator'),
        (OBSERVER, 'observer'),
        (RESIDENT, 'resident'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.SmallIntegerField(choices=ROLE_CHOICES)
