from defender.connection import get_redis_connection
from . import config, ip, users
REDIS_SERVER = get_redis_connection()

def is_already_locked(request, get_username=users.get_username_from_request, username=None):
    """Parse the username & IP from the request, and see if it's
    already locked."""
    user_blocked = users.is_already_locked(username or get_username(request))
    ip_blocked = ip.is_valid_ip(ip.get(request))

    if config.LOCKOUT_BY_IP_USERNAME:
        # if both this IP and this username are present the request is blocked
        return ip_blocked and user_blocked

    return ip_blocked or user_blocked

def strip_keys(key_list):
    """ Given a list of keys, remove the prefix and remove just
    the data we care about.

    for example:

        ['defender:blocked:ip:ken', 'defender:blocked:ip:joffrey']

    would result in:

        ['ken', 'joffrey']

    """
    return [key.split(":")[-1] for key in key_list]

def get_time():
    return int(config.COOLOFF_TIME / 60);

def increment_key(key):
    """ given a key increment the value """
    pipe = REDIS_SERVER.pipeline()
    pipe.incr(key, 1)
    if config.COOLOFF_TIME:
        pipe.expire(key, config.COOLOFF_TIME)
    new_value = pipe.execute()[0]
    return new_value

def get_attemps_left(request):
    return (config.FAILURE_LIMIT - users.get_user_attempts(request));