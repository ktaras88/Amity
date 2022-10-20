from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models

from localflavor.us.models import USStateField

from amity_api.settings import VALID_EXTENSIONS
from users.validators import phone_regex, validate_size

User = get_user_model()


class Community(models.Model):
    name = models.CharField('name', max_length=100)
    state = USStateField('state')
    zip_code = models.IntegerField('zip_code')
    address = models.CharField('address', max_length=100)
    contact_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    phone_number = models.CharField('phone number', validators=[phone_regex], max_length=20)
    description = models.CharField('description', max_length=100, null=True, blank=True)
    logo = models.ImageField('community logo', null=True, blank=True, upload_to='media/communities/', validators=[
        FileExtensionValidator(VALID_EXTENSIONS), validate_size])
    logo_coord = models.JSONField(null=True, blank=True)
    safety_status = models.BooleanField(default=True)
