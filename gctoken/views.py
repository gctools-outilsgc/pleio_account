"""
gctoken API endpoints
"""
from django.http import HttpResponseForbidden, HttpResponse
from jose import jwt
from django.views.decorators.clickjacking import xframe_options_exempt


# TODO: move the secret to a config file outside of git control
@xframe_options_exempt
def get_token(request):
    """
    If the user is authenticated, return a JWT token, otherwise return 403.
    """
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
          "window.parent.postMessage(\"%s\", 'http://gctools.lpss.me');" % encoded
        )
        response.write("</script></head><body></body></html>")
        return response
    else:
        return HttpResponseForbidden()
