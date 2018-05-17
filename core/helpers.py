import uuid
import os
from time import strftime
from urllib.parse import urlencode
from urllib.request import urlopen
from django.conf import settings
import requests

def unique_filepath(self, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('avatars/', filename)

def unique_avatar_large_filename(self, filename):
    ext = filename.split('.')[-1]
    filename = str('large.' + ext)
    return unique_avatar_filepath(self.user, filename)  

def unique_avatar_medium_filename(self, filename):
    ext = filename.split('.')[-1]
    filename = str('medium.' + ext)
    return unique_avatar_filepath(self.user, filename)  

def unique_avatar_small_filename(self, filename):
    ext = filename.split('.')[-1]
    filename = str('small.' + ext)
    return unique_avatar_filepath(self.user, filename)  

def unique_avatar_tiny_filename(self, filename):
    ext = filename.split('.')[-1]
    filename = str('tiny.' + ext)
    return unique_avatar_filepath(self.user, filename)  

def unique_avatar_topbar_filename(self, filename):
    ext = filename.split('.')[-1]
    filename = str('topbar.' + ext)
    return unique_avatar_filepath(self.user, filename)  

def unique_avatar_filepath(self, filename):
    result = os.path.join('avatars/', strftime('%Y/%m/%d'), str(self.id), filename)
    return result

def str_to_bool(s):
    if s == 'True':
        return True
    elif s == 'False':
        return False
    elif s:
        return True
    elif not s:
        return False
    else:
        return None

def verify_captcha_response(response):
    try:
        data = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': response
        }
    except AttributeError:
        return True

    if not response:
        return False

    try:
        result = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data).json()
        return result['success']

    except:
        return False