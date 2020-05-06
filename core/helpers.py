import os
import uuid

import requests
from django.conf import settings
from constance import config


def unique_filepath(self, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('avatars/', filename)


def verify_captcha_response(response):
    try:
        data = {
            'secret': config.RECAPTCHA_SECRET_KEY,
            'response': response
        }
    except AttributeError:
        return True

    try:
        result = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=data
        ).json()
        return result['success']
    except Exception:
        return False


def str_to_bool(s):
    if isinstance(s, str):
        if s.lower() == 'true':
            return True
    if isinstance(s, bool):
        if s:
            return True

    return False
