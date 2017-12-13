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

class PartnerSiteMiddleware(MiddlewareMixin):
    def process_response(self, request, response):

        try:
            if request.COOKIES['partner_site_url'] is None:
                request.COOKIES.pop['partner_site_url']
            partner_site_url = request.COOKIES['partner_site_url']
            response.set_cookie('partner_site_url', partner_site_url,
                path=settings.SESSION_COOKIE_PATH,
                secure=settings.SESSION_COOKIE_SECURE or None,
                httponly=settings.SESSION_COOKIE_HTTPONLY or None
            )
        except:
            try:
                response.delete_cookie('partner_site_url',
                path=settings.SESSION_COOKIE_PATH,
                )
            except:
                pass

        try:
            if request.COOKIES['partner_site_name'] is None:
                request.COOKIES.pop['partner_site_name']
            partner_site_name = request.COOKIES['partner_site_name']
            response.set_cookie('partner_site_name', partner_site_name,
                path=settings.SESSION_COOKIE_PATH,
                secure=settings.SESSION_COOKIE_SECURE or None,
                httponly=settings.SESSION_COOKIE_HTTPONLY or None
            )
        except:
            try:
                response.delete_cookie('partner_site_name',
                path=settings.SESSION_COOKIE_PATH,
                )
            except:
                pass

        try:
            if request.COOKIES['partner_site_logo_url'] is None:
                request.COOKIES.pop['partner_site_logo_url']
            partner_site_logo_url = request.COOKIES['partner_site_logo_url']
            response.set_cookie('partner_site_logo_url', partner_site_logo_url,
                path=settings.SESSION_COOKIE_PATH,
                secure=settings.SESSION_COOKIE_SECURE or None,
                httponly=settings.SESSION_COOKIE_HTTPONLY or None
            )
        except:
            try:
                response.delete_cookie('partner_site_logo_url',
                path=settings.SESSION_COOKIE_PATH,
                )
            except:
                pass

        return response