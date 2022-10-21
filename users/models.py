import random
from string import digits
from django.contrib.auth.models import AbstractBaseUser
from django.core.mail import send_mail
from django.core.validators import FileExtensionValidator
from django.db import models
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from rest_framework.authtoken.models import Token

from amity_api.settings import EMAIL_HOST_USER, FRONT_END_NEW_PASSWORD_URL, VALID_EXTENSIONS
from .choices_types import ProfileRoles
from .managers import UserManager
from .validators import phone_regex, validate_size


class InvitationToken(Token):
    type = models.CharField(max_length=20, default="invitation")


class User(AbstractBaseUser):
    def file_path(instance, filename):
        return 'media/avatars/' + str(instance.id)

    first_name = models.CharField('first name', max_length=100)
    last_name = models.CharField('last name', max_length=100)
    email = models.EmailField('email address', unique=True, db_index=True)
    phone_number = models.CharField('phone number', validators=[phone_regex], max_length=20)
    password = models.CharField('password', max_length=100, null=True, blank=True)
    avatar = models.ImageField('user avatar', null=True, blank=True, upload_to=file_path, validators=[
        FileExtensionValidator(VALID_EXTENSIONS), validate_size])
    avatar_coord = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    security_code = models.CharField(max_length=6, default=None, null=True, blank=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def create_profile(self, role):
        Profile.objects.create(user_id=self.id, role=role)

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff

    def generate_security_code(self, length=6):
        return ''.join(random.sample(digits, length))

    def send_security_code(self):
        self.security_code = self.generate_security_code()
        self.save()

        context = {
            'first_name': self.first_name,
            'second_name': self.last_name,
            'security_code': self.security_code
        }

        subject = 'Amity security code'
        html = render_to_string('email_security_code.html', context=context)
        message = strip_tags(html)

        send_mail(subject, message, EMAIL_HOST_USER, [self.email], html_message=html)

    def send_invitation_link(self):
        token = InvitationToken.objects.create(user=self)

        context = {
            'first_name': self.first_name,
            'second_name': self.last_name,
            'link_url': FRONT_END_NEW_PASSWORD_URL + '?token=' + str(token)
        }

        subject = 'Invitation to Amity password creation'
        html = render_to_string('invitation_to_amity_system.html', context=context)
        message = strip_tags(html)

        send_mail(subject, message, EMAIL_HOST_USER, [self.email], html_message=html)

    def __str__(self):
        return self.get_full_name()


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.SmallIntegerField(choices=ProfileRoles.CHOICES)

    class Meta:
        unique_together = ['user', 'role']
        