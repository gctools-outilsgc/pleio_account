from .users import get_username_from_request
from . import ip,attemps

def check(request, login_unsuccessful,
                  get_username=get_username_from_request,
                  username=None):
    """ check the request, and process results"""
    ip_address = ip.get(request)
    username = username or get_username(request)

    if not login_unsuccessful:
        # user logged in -- forget the failed attempts
        attemps.reset_failed(ip_address=ip_address, username=username)
        return True
    else:
        # add a failed attempt for this user
        return attemps.record_failed(request,ip_address, username)

