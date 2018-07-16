import string
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import views as auth_views
from django.utils.decorators import method_decorator
from pleio_account.decorators import watch_login

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
        self.handle_partner_site_cookie(request, response, 'partner_site_url')
        self.handle_partner_site_cookie(request, response, 'partner_site_name')
        self.handle_partner_site_cookie(request, response, 'partner_site_logo_url')

        return response

    def handle_partner_site_cookie(self, request, response, acookie):
        try:
            if request.COOKIES[acookie] is None:
                request.COOKIES.pop[acookie]
            partner_site_url = request.COOKIES[acookie]
            response.set_cookie(acookie, partner_site_url,
                path=settings.SESSION_COOKIE_PATH,
                secure=settings.SESSION_COOKIE_SECURE or None,
                httponly=settings.SESSION_COOKIE_HTTPONLY or None
            )
        except:
            try:
                response.delete_cookie(acookie,
                path=settings.SESSION_COOKIE_PATH,
                )
            except:
                pass

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


class FailedLoginMiddleware(MiddlewareMixin):
    """ Failed login middleware """
    patched = False
    # Monkey-patch only once - otherwise we would be recording
    # failed attempts multiple times!

    def process_response(self, request, response):
        if not FailedLoginMiddleware.patched:
            try:
                from core.class_views import PleioLoginView
                our_decorator = watch_login()
                watch_login_method = method_decorator(our_decorator)
                PleioLoginView.dispatch = watch_login_method(PleioLoginView.dispatch)

            except ImportError:
                auth_views.login = watch_login()(auth_views.login)

            FailedLoginMiddleware.patched = True
            return response
            
        return response