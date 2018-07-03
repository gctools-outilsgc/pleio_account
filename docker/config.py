import os
from django.utils.translation import ugettext_lazy as _
from core.helpers import str_to_bool
from urllib.parse import urljoin

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = str_to_bool(os.getenv('DEBUG'))

EXTERNAL_HOST = os.getenv('EXTERNAL_HOST')

# Include apps required before any other apps, like themes.
LOCAL_INSTALLED_APPS = os.getenv('LOCAL_INSTALLED_APPS', '').split(',')

LOCAL_AUTHENTICATION_BACKENDS = os.getenv('LOCAL_INSTALLED_APPS', '').split(',')

LOCAL_AUTH_PASSWORD_VALIDATORS = os.getenv('LOCAL_AUTH_PASSWORD_VALIDATORS', '').split(',')

# SECURITY WARNING: set this to True when running in production
SESSION_COOKIE_SECURE = str_to_bool(os.getenv('SESSION_COOKIE_SECURE'))
SESSION_COOKIE_HTTPONLY = str_to_bool(os.getenv('SESSION_COOKIE_HTTPONLY'))

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

TIME_ZONE = os.getenv('TIME_ZONE', 'GMT')

LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'en')

LANGUAGES = [
    ('en', _('English')),
    ('nl', _('Dutch')),
    ('fr', _('French'))
]

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL')

SITE_TITLE = os.getenv('SITE_TITLE', 'Concierge')
SITE_LOGO = os.getenv('SITE_LOGO', 'images/logo.svg')
SITE_FAVICON = os.getenv('SITE_FAVICON', 'images/favicon.svg')
EMAIL_LOGO = os.getenv('EMAIL_LOGO', 'images/email-logo.png')

SHOW_GOVERNMENT_BADGE = os.getenv('SEND_SUSPICIOUS_BEHAVIOR_WARNINGS', True)
SEND_SUSPICIOUS_BEHAVIOR_WARNINGS = os.getenv('SEND_SUSPICIOUS_BEHAVIOR_WARNINGS', True)

PASSWORD_RESET_TIMEOUT_DAYS = 1
ACCOUNT_ACTIVATION_DAYS = 7

# For use with mod_pleio Elgg plugin
ELGG_URL = os.getenv('ELGG_URL')
ELGG_DB_URL = os.getenv('ELGG_DB_URL')

SITE_URL = os.getenv('SITE_URL', None)
CORS_ORIGIN_WHITELIST = os.getenv('CORS_ORIGIN_WHITELIST', '').split(',')

RECAPTCHA_MINUTES_THRESHOLD = 30
RECAPTCHA_NUMBER_INVALID_LOGINS = 10

GOOGLE_RECAPTCHA_SITE_KEY = os.getenv('GOOGLE_RECAPTCHA_SITE_KEY')
GOOGLE_RECAPTCHA_SECRET_KEY = os.getenv('GOOGLE_RECAPTCHA_SECRET_KEY')

SAML2_SP = {
    "entityId": urljoin(os.getenv('EXTERNAL_HOST'), 'saml/metadata/'),
    "assertionConsumerService": {
        "url": urljoin(os.getenv('EXTERNAL_HOST'), 'saml/acs/'),
        "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    },
    "singleLogoutService": {
        "url": urljoin(os.getenv('EXTERNAL_HOST'), 'saml/slo/'),
        "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    },
    "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
    "x509cert": os.getenv("SAML_SP_X509CERT"),
    "privateKey": os.getenv("SAML_SP_PRIVATEKEY")
}

# Setting CELERY_ALWAYS_EAGER to "True"  will make task being executed locally in the client, not by a worker.
# Always use "False" in production environment.
CELERY_ALWAYS_EAGER = True
CELERY_BROKER_URL = "amqp://localhost"

# Dummy commit to force rebuild in GitHub
