from defender import config as def_config
from defender.connection import get_redis_connection
from defender.signals import send_ip_block_signal
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv46_address

REDIS_SERVER = get_redis_connection()


def get(request):
    """ get the ip address from the request """
    if def_config.BEHIND_REVERSE_PROXY:
        ip_address = request.META.get(def_config.REVERSE_PROXY_HEADER, '')
        ip_address = ip_address.split(",", 1)[0].strip()
        if ip_address == '':
            ip_address = get_from_request(request)
    else:
        ip_address = get_from_request(request)
    return ip_address


def block(ip_address):
    """ given the ip, block it """
    if not ip_address:
        # no reason to continue when there is no ip
        return
    if def_config.DISABLE_IP_LOCKOUT:
        # no need to block, we disabled it.
        return
    key = get_blocked_cache_key(ip_address)
    if def_config.COOLOFF_TIME:
        REDIS_SERVER.set(key, 'blocked', def_config.COOLOFF_TIME)
    else:
        REDIS_SERVER.set(key, 'blocked')
    send_ip_block_signal(ip_address)


def unblock(ip_address, pipe=None):
    """ unblock the given IP """
    do_commit = False
    if not pipe:
        pipe = REDIS_SERVER.pipeline()
        do_commit = True
    if ip_address:
        pipe.delete(get_attempt_cache_key(ip_address))
        pipe.delete(get_blocked_cache_key(ip_address))
        if do_commit:
            pipe.execute()


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


def get_attempt_cache_key(ip_address):
    """ get the cache key by ip """
    return "{0}:failed:ip:{1}".format(def_config.CACHE_PREFIX, ip_address)


def get_blocked_cache_key(ip_address):
    """ get the cache key by ip """
    return "{0}:blocked:ip:{1}".format(def_config.CACHE_PREFIX, ip_address)


def is_source_already_locked(ip_address):
    """Is this IP already locked?"""
    if ip_address is None:
        return False
    if def_config.DISABLE_IP_LOCKOUT:
        return False
    return REDIS_SERVER.get(get_blocked_cache_key(ip_address))