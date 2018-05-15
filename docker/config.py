import os
import sys

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG')

SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE')

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

if 'test' in sys.argv or 'test_coverage' in sys.argv:
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

STATIC_ROOT = '/app/static'

LANGUAGE_CODE = 'nl-nl'

TIME_ZONE = 'Europe/Amsterdam'

STATIC_ROOT = '/app/static'

EXTERNAL_HOST = os.getenv('EXTERNAL_HOST')
EMAIL_LOGO = os.getenv('EMAIL_LOGO', 'images/email-logo.png')

SITE_TITLE = os.getenv('SITE_TITLE', 'Pleio account')
SITE_LOGO = os.getenv('SITE_LOGO', 'images/logo.svg')
SITE_FAVICON = os.getenv('SITE_FAVICON', 'images/favicon.svg')

SEND_SUSPICIOUS_BEHAVIOR_WARNINGS = os.getenv('SEND_SUSPICIOUS_BEHAVIOR_WARNINGS')

DEFAULT_FROM_EMAIL = os.getenv('FROM_EMAIL')

# Used for testing without SMTP
# EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL')

SITE_URL = os.getenv('SITE_URL', None)
CORS_ORIGIN_WHITELIST = os.getenv('CORS_ORIGIN_WHITELIST', '').split(',')

GOOGLE_RECAPTCHA_SITE_KEY = os.getenv('GOOGLE_RECAPTCHA_SITE_KEY')
GOOGLE_RECAPTCHA_SECRET_KEY = os.getenv('GOOGLE_RECAPTCHA_SECRET_KEY')
