import time

from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models

from localflavor.us.models import USStateField

from amity_api.settings import VALID_EXTENSIONS
from buildings.models import Building
from users.validators import phone_regex, validate_size

User = get_user_model()


class Community(models.Model):
    def file_path(self, filename):
        return 'media/communities/' + str(self.id) + str(time.time())

    name = models.CharField('name', max_length=100)
    state = USStateField('state')
    zip_code = models.IntegerField('zip_code')
    address = models.CharField('address', max_length=100)
    contact_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='communities')
    phone_number = models.CharField('phone number', validators=[phone_regex], max_length=20)
    description = models.CharField('description', max_length=100, null=True, blank=True)
    logo = models.ImageField('community logo', null=True, blank=True, upload_to=file_path, validators=[
        FileExtensionValidator(VALID_EXTENSIONS), validate_size])
    logo_coord = models.JSONField(null=True, blank=True)
    safety_status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def switch_safety_status(self):
        self.safety_status = not self.safety_status
        self.save()
        Building.objects.filter(community=self.id).update(safety_status=self.safety_status)

    def create_recent_activity_record(self, user_id, activity):
        RecentActivity.objects.create(community=self,
                                      user_id=user_id,
                                      activity=activity,
                                      status=self.safety_status)


class RecentActivity(models.Model):
    SAFETY_STATUS = 1
    MASTER_OFF = 2
    ACTIVITY_CHOICES = ((SAFETY_STATUS, "safety_status"), (MASTER_OFF, "master_off"),)

    community = models.ForeignKey(Community, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    switch_time = models.DateTimeField(auto_now_add=True)
    activity = models.CharField('activity', choices=ACTIVITY_CHOICES, max_length=15)
    status = models.BooleanField()
