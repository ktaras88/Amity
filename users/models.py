import random
from string import digits
from django.contrib.auth.models import AbstractBaseUser
from django.core.mail import send_mail
from django.core.validators import RegexValidator, FileExtensionValidator
from django.db import models
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

from amity_api.settings import EMAIL_HOST_USER, FRONT_END_NEW_PASSWORD_URL, VALID_EXTENSIONS
from .choices_types import ProfileRoles
from .managers import UserManager


class InvitationToken(Token):
    type = models.CharField(max_length=20, default="invitation")


class User(AbstractBaseUser):
    phone_regex = RegexValidator(
        regex=r"^+?1?\d{10,15}$",
        message="Phone number must be entered in the format: "
                "'+999999999'. Up to 15 digits allowed.",
    )

    def validate_size(fieldfile_obj):
        filesize = fieldfile_obj.size
        megabyte_limit = 5.0
        if filesize > megabyte_limit * 1024 * 1024:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    def file_name(instance, filename):
        return 'media/avatars/' + str(instance.id) + '_' + str(instance.email)

    first_name = models.CharField('first name', max_length=100, null=True, blank=True)
    last_name = models.CharField('last name', max_length=100, null=True, blank=True)
    email = models.EmailField('email address', unique=True, db_index=True)
    phone_number = models.CharField('phone number', validators=[phone_regex], max_length=20, null=True, blank=True)
    password = models.CharField('password', max_length=100, null=True, blank=True)
    avatar = models.ImageField('user avatar', null=True, blank=True, upload_to=file_name, validators=[
        FileExtensionValidator(VALID_EXTENSIONS), validate_size])
    avatar_coord = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    security_code = models.CharField(max_length=6, default=None, null=True, blank=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'

    def create_profile(self, role):
        Profile.objects.create(user_id=self.id, role=role)

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff

    def generate_security_code(self, length=6):
        return ''.join(random.choice(digits) for _ in range(length))

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


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.SmallIntegerField(choices=ProfileRoles.CHOICES)

    class Meta:
        unique_together = ['user', 'role']
        