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
    # 'elgg',
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

DEFAULT_FROM_EMAIL = 'concierge@hil.ton'

EMAIL_HOST = 'localhost'
EMAIL_PORT = 25

SITE_TITLE = 'Concierge'
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
ELGG_DB_URL = ''

# Google reCAPTCHA Will be present on login page when from that IP adress more than RECAPTCHA_NUMBER_INVALID_LOGINS during the last RECAPTCHA_MINUTES_THRESHOLD have occurred.
# Request an API key at https://developers.google.com/recaptcha/ for reCAPTCHA validation.
RECAPTCHA_MINUTES_THRESHOLD = 30
RECAPTCHA_NUMBER_INVALID_LOGINS = 10

# With the following test keys, you will always get No CAPTCHA and all verification requests will pass.
GOOGLE_RECAPTCHA_SITE_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
GOOGLE_RECAPTCHA_SECRET_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'

SAML2_SP = {
    "entityId": "http://172.17.0.1:8000/saml/metadata/",
    "assertionConsumerService": {
        "url": "http://172.17.0.1:8000/saml/acs/",
        "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    },
    "singleLogoutService": {
        "url": "http://172.17.0.1:8000/saml/slo/",
        "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    },
    "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
    "x509cert": "MIICUjCCAbugAwIBAgIBADANBgkqhkiG9w0BAQ0FADBGMQswCQYDVQQGEwJubDEQMA4GA1UECAwHVXRyZWNodDEOMAwGA1UECgwFUGxlaW8xFTATBgNVBAMMDHd3dy5wbGVpby5ubDAeFw0xODAxMzAxMzU0MzdaFw0xOTAxMzAxMzU0MzdaMEYxCzAJBgNVBAYTAm5sMRAwDgYDVQQIDAdVdHJlY2h0MQ4wDAYDVQQKDAVQbGVpbzEVMBMGA1UEAwwMd3d3LnBsZWlvLm5sMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCy2HWJ7r9rED7Femo32cgmcV1vSzkJarE5oS1HKkTwPRoXJK3TFU9CeF45GOOvpEcxcCZkz+e0JeU3+8lir+fhu2aZsNSqdPc56qrHsQk0/EkzPLIfUe0pVI0OSnAm82X43RWw0Jl/46U8ZUcpzuM2ltswkRBIr1o3eRyuyR83HwIDAQABo1AwTjAdBgNVHQ4EFgQUYOL49JvyZjjaomA4RnsVjKGAKOEwHwYDVR0jBBgwFoAUYOL49JvyZjjaomA4RnsVjKGAKOEwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQ0FAAOBgQAfn+7GQQ1Lq2ZhGMc219U1/kbOIZuaTwCw0IVluoxLy5kzqY2huV/gl8UUFr3Inp/VoX1eUmOK5WFtbHRj79AP6NX7A1B9OBcQDMFI2kJDhZQc1+5JFuwLPElrdZYyuSoB5Ey/CMbAkicZjxPWwutn34on3erPDYkmAvn74kl9og==",
    "privateKey": ""
}

# Setting CELERY_ALWAYS_EAGER to "True"  will make task being executed locally in the client, not by a worker.
# Always use "False" in production environment.
CELERY_ALWAYS_EAGER = True
CELERY_BROKER_URL = "amqp://localhost"

OIDC_EXTRA_SCOPE_CLAIMS = 'concierge.oidc_provider_settings.CustomScopeClaims'
