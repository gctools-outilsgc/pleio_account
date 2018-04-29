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

LANGUAGE_CODE = 'en'

TIME_ZONE = 'America/Toronto'

STATIC_ROOT = '/app/static'

SEND_SUSPICIOUS_BEHAVIOR_WARNINGS = os.getenv('SEND_SUSPICIOUS_BEHAVIOR_WARNINGS')

DEFAULT_FROM_EMAIL = os.getenv('FROM_EMAIL')

#EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL')

SITE_URL = os.getenv('SITE_URL', None)
CORS_ORIGIN_WHITELIST = os.getenv('CORS_ORIGIN_WHITELIST', '').split(',')

DEFENDER_LOGIN_FAILURE_LIMIT = 3
DEFENDER_BEHIND_REVERSE_PROXY= False
DEFENDER_DISABLE_IP_LOCKOUT = True
DEFENDER_COOLOFF_TIME = 600
DEFENDER_LOCKOUT_URL = 'https://i1.wp.com/idrathertalk.com/wp-content/uploads/2016/08/Blocked-Out-Locked-Out-with-eviction-notice-2017-logo.jpg'
DEFENDER_REDIS_URL = 'redis://cache:6379/0'
DEFENDER_ACCESS_ATTEMPT_EXPIRATION =24
DEFENDER_USERNAME_FORM_FIELD = 'auth-username'
