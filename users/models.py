from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models

from .choices_types import ProfileRoles
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
    objects = UserManager()

    USERNAME_FIELD = 'email'

    def create_profile(self, role):
        Profile.objects.create(user_id=self.id, role=role)

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.SmallIntegerField(choices=ProfileRoles.CHOICES)

    class Meta:
        unique_together = ['user', 'role']
