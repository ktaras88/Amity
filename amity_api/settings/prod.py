import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from decouple import config

from .base import *


DEBUG = config('DEBUG', default=False)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default=''),
        'USER': config('DB_USER_NAME', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='db'),
        'PORT': '5432',
    }
}

sentry_sdk.init(
    dsn=config('DSN_KEY', default=''),
    integrations=[
        DjangoIntegration(),
    ],
    traces_sample_rate=1.0,
    send_default_pii=True
)

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
AWS_QUERYSTRING_AUTH = False
