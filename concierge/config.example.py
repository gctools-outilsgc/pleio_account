import os
from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'HWZUzWbMVAnzdwJxeYnACTazALmQ8b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

EXTERNAL_HOST = 'http://127.0.0.1:8000/'

# Include apps required before any other apps, like themes.
LOCAL_INSTALLED_APPS = [
    # 'concierge_theme_gc',
    # 'concierge_theme_pleio',
]

LOCAL_AUTHENTICATION_BACKENDS = [
    # 'elgg.backends.ElggBackend'
]

LOCAL_AUTH_PASSWORD_VALIDATORS = []

# SECURITY WARNING: set this to True when running in production
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

TIME_ZONE = 'GMT'

LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', _('English')),
    ('nl', _('Dutch')),
    ('fr', _('French'))
]

FROM_EMAIL = 'concierge@hil.ton'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25

SITE_TITLE = 'Pleio account'
SITE_LOGO = 'images/logo.svg'
SITE_FAVICON = 'images/favicon.png'
EMAIL_LOGO = 'images/email-logo.png'

#This setting controls whether an image should be displayed when a user is also a member of other group(s) than "Any"
SHOW_GOVERNMENT_BADGE = True

# Send users a warning message when suspicious behaviour on their account occurs, e.g. a login on the account from a new (unknown) location.
SEND_SUSPICIOUS_BEHAVIOR_WARNINGS = True

PASSWORD_RESET_TIMEOUT_DAYS = 1
ACCOUNT_ACTIVATION_DAYS = 7

# For use with mod_pleio Elgg plugin
ELGG_URL = ''

# Google reCAPTCHA Will be present on login page when from that IP adress more than RECAPTCHA_NUMBER_INVALID_LOGINS during the last RECAPTCHA_MINUTES_THRESHOLD have occurred.
# Request an API key at https://developers.google.com/recaptcha/ for reCAPTCHA validation.
RECAPTCHA_MINUTES_THRESHOLD = 30
RECAPTCHA_NUMBER_INVALID_LOGINS = 10

# With the following test keys, you will always get No CAPTCHA and all verification requests will pass.
GOOGLE_RECAPTCHA_SITE_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
GOOGLE_RECAPTCHA_SECRET_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'
