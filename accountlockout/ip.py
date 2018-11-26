from django.core.validators import validate_ipv46_address
from django.core.exceptions import ValidationError
from . import config

def get(request):
    """ get the ip address from the request """
    if config.BEHIND_REVERSE_PROXY:
        ip_address = request.META.get(config.REVERSE_PROXY_HEADER, '')
        ip_address = ip_address.split(",", 1)[0].strip()
        if ip_address == '':
            ip_address = get_from_request(request)
    else:
        ip_address = get_from_request(request)
    return ip_address

def get_from_request(request):
    """ Makes the best attempt to get the client's real IP or return
        the loopback """
    remote_addr = request.META.get('REMOTE_ADDR', '')
    if remote_addr and is_valid_ip(remote_addr):
        return remote_addr.strip()
    return '127.0.0.1'

def is_valid_ip(ip_address):
    """ Check Validity of an IP address """
    if not ip_address:
        return False
    ip_address = ip_address.strip()
    try:
        validate_ipv46_address(ip_address)
        return True
    except ValidationError:
        return False