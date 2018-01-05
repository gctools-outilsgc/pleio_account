"""
gctoken API endpoints
"""
from urllib.parse import urlparse, urlencode
import urllib.request
import re

from django.http import HttpResponseForbidden, HttpResponse, \
    HttpResponseBadRequest
from django.views.decorators.clickjacking import xframe_options_exempt
from django.conf import settings

from jose import jwt

ALLOWED_TOKEN_ORIGINS = [
    'http://gcrec.lpss.me',
    'http://gctools.lpss.me',
    'https://gcrec.lpss.me',
    'https://gctools.lpss.me',
    'http://localhost:3001'
]


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

    encoded = ''

    if request.user.is_authenticated():
        # HACK: Temporary to get gconnex guid
        search_url = "http://intranet.canada.ca/search-recherche/" \
                     "query-recherche-eng.aspx?a=s&s=3&chk4=on&%s" \
                     % urlencode({'q': request.user.email})
        with urllib.request.urlopen(search_url) as response:
            search_html = response.read()
            username_match = re.search(
                'href="https://gcconnex.gc.ca/profile/(.*?)"',
                search_html.decode('utf-8')
            )
            username = 'N/A'
            guid = 'N/A'
            if username_match:
                username = username_match.group(1)
                profile_url = "https://gcconnex.gc.ca/profile/%s" % username
                with urllib.request.urlopen(profile_url) as profile_response:
                    profile_html = profile_response.read()
                    guid_match = re.search(
                        '"guid":(.*?),',
                        profile_html.decode('utf-8')
                    )
                    if guid_match:
                        guid = guid_match.group(1)

        encoded = jwt.encode(
            {
                'email': request.user.email,
                'gcconnex_username': username,
                'gcconnex_guid': guid
            },
            settings.GCTOKEN_SECRET,
            algorithm='HS256'
        )
    else:
        encoded = jwt.encode(
            {
                'email': '',
                'gcconnex_username': '',
                'gcconnex_guid': '-1'
            },
            settings.GCTOKEN_SECRET,
            algorithm='HS256'
        )
    response = HttpResponse()
    response.write("<html><head><script type=\"text/javascript\">\n")
    response.write(
        "window.parent.postMessage(\"%s\", '%s');" % (encoded, origin)
    )
    response.write("</script></head><body></body></html>")
    return response
