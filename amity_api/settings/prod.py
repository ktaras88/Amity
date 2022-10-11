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
