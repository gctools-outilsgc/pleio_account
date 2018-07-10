import os
from core.helpers import str_to_bool

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = str_to_bool(os.getenv('DEBUG'))

ALLOWED_HOSTS = [os.getenv('ALLOWED_HOST')]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.getenv('DB_HOST'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'NAME': os.getenv('DB_NAME'),
    }
}

STATIC_ROOT = '/app/static'

LANGUAGE_CODE = 'en'

TIME_ZONE = 'America/Toronto'

STATIC_ROOT = '/app/static'

DEFAULT_FROM_EMAIL = os.getenv('FROM_EMAIL')

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL')

SITE_URL = os.getenv('SITE_URL', None)
CORS_ORIGIN_WHITELIST = os.getenv('CORS_ORIGIN_WHITELIST', '').split(',')

SESSION_COOKIE_SECURE = str_to_bool(os.getenv('SECURE_SESSION', True))
SESSION_COOKIE_HTTPONLY = True


GRAPHQL_TRIGGERS = True
GRAPHQL_ENDPOINT = 'https://graphql.gccollab.ca/protected'
GRAPHQL_TOKEN = 'aeb69b36cc2d332be878887971a61bf16411c3c0'
