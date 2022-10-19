from django.core.validators import RegexValidator
from django.db import models
from localflavor.us.models import USStateField

from users.models import User


class Community(models.Model):

    phone_regex = RegexValidator(
        regex=r"^+?1?\d{10,15}$",
        message="Phone number must be entered in the format: "
                "'+999999999'. Up to 15 digits allowed.",
    )

    name = models.CharField('name', max_length=100)
    state = USStateField('state')
    zip_code = models.IntegerField('zip_code')
    address = models.CharField('address', max_length=100)
    contact_person = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contact_person', null=True, blank=True)
    phone_number = models.CharField('phone number', validators=[phone_regex], max_length=20)
    description = models.CharField('description', max_length=100, null=True, blank=True)
    logo = models.ImageField('community logo', null=True, blank=True, upload_to='media/')
    logo_coord = models.JSONField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by')
    safety_status = models.BooleanField(default=False)
