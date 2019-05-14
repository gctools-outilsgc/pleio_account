import os
from core.helpers import str_to_bool

DEBUG = str_to_bool(os.getenv('DEBUG'))

STATIC_ROOT = '/app/static'

LANGUAGE_CODE = 'en'

TIME_ZONE = 'America/Toronto'

STATIC_ROOT = '/app/static'

SITE_URL = os.getenv('SITE_URL', None)
CORS_ORIGIN_WHITELIST = os.getenv('CORS_ORIGIN_WHITELIST', '').split(',')

SESSION_COOKIE_SECURE = str_to_bool(os.getenv('SECURE_SESSION', True))
SESSION_COOKIE_HTTPONLY = True
