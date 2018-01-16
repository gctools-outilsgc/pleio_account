import string
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils.deprecation import MiddlewareMixin

VALID_KEY_CHARS = string.ascii_lowercase + string.digits

class DeviceIdMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        try:
            device_id = request.COOKIES['device_id']
            if len(device_id) != 32:
                raise KeyError
        except KeyError:
            device_id = get_random_string(32, VALID_KEY_CHARS)

        max_age = 365 * 24 * 60 * 60  # one year
        response.set_cookie('device_id', device_id,
            max_age=max_age,
            path=settings.SESSION_COOKIE_PATH,
            secure=settings.SESSION_COOKIE_SECURE or None,
            httponly=settings.SESSION_COOKIE_HTTPONLY or None
        )

        return response

class XRealIPMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            real_ip = request.META['HTTP_X_REAL_IP']
        except KeyError:
            pass
        else:
            request.META['REMOTE_ADDR'] = real_ip
        return self.get_response(request)
