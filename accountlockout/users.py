from django.utils.module_loading import import_string
from defender.connection import get_redis_connection
from defender.signals import send_username_block_signal
from . import config, utils, ip
REDIS_SERVER = get_redis_connection()

get_username_from_request = import_string(
    config.GET_USERNAME_FROM_REQUEST_PATH
)

def lower(username):
    """
    Single entry point to force the username to lowercase, all the functions
    that need to deal with username should call this.
    """
    if username:
        try:
            username = username.lower()
        except:
            username = username
    return username

def unblock(username, pipe=None):
    """ unblock the given Username """
    do_commit = False
    if not pipe:
        pipe = REDIS_SERVER.pipeline()
        do_commit = True
    if username:
        pipe.delete(get_attempt_cache_key(username))
        pipe.delete(get_blocked_cache_key(username))
        if do_commit:
            pipe.execute()

def block(username):
    """ given the username block it. """
    if not username:
        # no reason to continue when there is no username
        return
    if config.DISABLE_USERNAME_LOCKOUT:
        # no need to block, we disabled it.
        return
    key = get_blocked_cache_key(username)
    if config.COOLOFF_TIME:
        REDIS_SERVER.set(key, 'blocked', config.COOLOFF_TIME)
    else:
        REDIS_SERVER.set(key, 'blocked')
    send_username_block_signal(username)

def get_from_request(request):
    """ unloads username from default POST request """
    if config.USERNAME_FORM_FIELD in request.POST:
        return request.POST[config.USERNAME_FORM_FIELD][:255]
    return None

def is_already_locked(username):
    """Is this username already locked?"""
    if username is None:
        return False
    if config.DISABLE_USERNAME_LOCKOUT:
        return False
    return REDIS_SERVER.get(get_blocked_cache_key(username))

def is_source_ip_already_locked(ip_address):
    """Is this IP already locked?"""
    if ip_address is None:
        return False
    if config.DISABLE_IP_LOCKOUT:
        return False
    return REDIS_SERVER.get(get_blocked_cache_key(ip_address))

def get_user_attempts(request, get_username=get_username_from_request, username=None):
    """ Returns number of access attempts for this ip, username
    """
    ip_address = ip.get(request)
    username = lower(username or get_username(request))
    # get by IP
    ip_count = REDIS_SERVER.get(ip.get_attempt_cache_key(ip_address))
    if not ip_count:
        ip_count = 1
    else:
        # we add 1 to the Redis count because the Redis index starts at 0
        ip_count = int(ip_count) + 1

    # get by username
    username_count = REDIS_SERVER.get(get_attempt_cache_key(username))
    if not username_count:
        username_count = 1
    else:
        # we add 1 to the Redis count because the Redis index starts at 0
        username_count = int(username_count) + 1
    # return the larger of the two.
    return max(ip_count, username_count)

def get_blocked_usernames():
    """ get a list of blocked usernames from redis """
    if config.DISABLE_USERNAME_LOCKOUT:
        # There are no blocked usernames since we disabled them.
        return []
    key = get_blocked_cache_key("*")
    key_list = [redis_key.decode('utf-8')
                for redis_key in REDIS_SERVER.keys(key)]
    return utils.strip_keys(key_list)

def get_attempt_cache_key(username):
    """ get the cache key by username """
    return "{0}:failed:username:{1}".format(config.CACHE_PREFIX, lower(username))

def get_blocked_cache_key(username):
    """ get the cache key by username """
    return "{0}:blocked:username:{1}".format(config.CACHE_PREFIX, lower(username))