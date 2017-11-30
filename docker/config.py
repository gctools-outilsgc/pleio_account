import os

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG')

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

LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'nl-nl')

TIME_ZONE = os.getenv('TIME_ZONE', 'Europe/Amsterdam')

STATIC_ROOT = '/app/static'

CHECK_PREVIOUS_LOGINS = os.getenv('CHECK_PREVIOUS_LOGINS')

DEFAULT_FROM_EMAIL = os.getenv('FROM_EMAIL')

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL')

GCTOKEN_SECRET = os.getenv('GCTOKEN_SECRET')

SEND_SUSPICIOUS_BEHAVIOR_WARNINGS \
    = os.getenv('SEND_SUSPICIOUS_BEHAVIOR_WARNINGS', 'f').lower() in [
        'true', '1', 't', 'y', 'yes', 'on'
    ]
