"""
gctoken API endpoints
"""
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseBadRequest
from jose import jwt
from django.views.decorators.clickjacking import xframe_options_exempt
from urllib.parse import urlparse

ALLOWED_TOKEN_ORIGINS = [
    'http://gcrec.lpss.me',
    'http://gctools.lpss.me',
    'https://gcrec.lpss.me',
    'https://gctools.lpss.me',
    'http://localhost:3001'
]


# TODO: move the secret to a config file outside of git control
@xframe_options_exempt
def get_token(request):
    """
    If the user is authenticated, return a JWT token, otherwise return 403.
    Additionally returns 403 unless the origin is trusted.
    """
    if 'HTTP_REFERER' not in request.META:
        return HttpResponseBadRequest()

    parsed = urlparse(request.META['HTTP_REFERER'])
    origin = "%s://%s" % (parsed.scheme, parsed.hostname)
    if parsed.port is not None:
        origin += ':%s' % parsed.port
    if origin not in ALLOWED_TOKEN_ORIGINS:
        return HttpResponseForbidden()

    if request.user.is_authenticated():
        encoded = jwt.encode(
            {
                'email': request.user.email,
                'gcconnex_guid': '24294737'
            },
            'dXSAKDCEE#KJFE@KF$(ITRE@de2hf8432yfujefd42F',
            algorithm='HS256'
        )
        response = HttpResponse()
        response.write("<html><head><script type=\"text/javascript\">\n")
        response.write(
          "window.parent.postMessage(\"%s\", '%s');" % (encoded, origin)
        )
        response.write("</script></head><body></body></html>")
        return response
    else:
        return HttpResponseForbidden()
