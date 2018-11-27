from .helper import ip_helper, attemps_helper
from .helper.defender_vars import get_username_from_request


def check(request, login_unsuccessful, get_username=get_username_from_request,
          username=None):
    """ check the request, and process results"""
    ip_address = ip_helper.get(request)
    username = username or get_username(request)
    if not login_unsuccessful:
        # user logged in -- forget the failed attempts
        attemps_helper.reset_failed(ip_address=ip_address, username=username)
        return True
    else:
        # add a failed attempt for this user
        return attemps_helper.record_failed(request, ip_address, username)
