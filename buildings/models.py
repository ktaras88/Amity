from django.contrib.auth import get_user_model
from django.db import models

from localflavor.us.models import USStateField

from communities.models import Community
from users.validators import phone_regex

User = get_user_model()


class Building(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    name = models.CharField('name', max_length=100)
    state = USStateField('state')
    address = models.CharField('address', max_length=100)
    contact_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    phone_number = models.CharField('phone number', validators=[phone_regex], max_length=20, null=True, blank=True)
    safety_status = models.BooleanField(default=True)
