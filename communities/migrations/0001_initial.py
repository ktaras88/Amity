# Generated by Django 4.1.1 on 2022-10-20 11:39

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import localflavor.us.models
import users.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Community',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('state', localflavor.us.models.USStateField(max_length=2, verbose_name='state')),
                ('zip_code', models.IntegerField(verbose_name='zip_code')),
                ('address', models.CharField(max_length=100, verbose_name='address')),
                ('phone_number', models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^+?1?\\d{10,15}$')], verbose_name='phone number')),
                ('description', models.CharField(blank=True, max_length=100, null=True, verbose_name='description')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='media/communities/', validators=[django.core.validators.FileExtensionValidator(['jpg', 'png', 'jpeg']), users.validators.validate_size], verbose_name='community logo')),
                ('logo_coord', models.JSONField(blank=True, null=True)),
                ('safety_status', models.BooleanField(default=True)),
                ('contact_person', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]