from .base import *
from decouple import config

DEBUG = config('DEBUG', default=True)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default=''),
        'USER': config('DB_USER_NAME', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='db'),
        'PORT': config('DB_PORT', default=''),
    }
}
