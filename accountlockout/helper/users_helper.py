from defender import config as def_config
from defender.signals import send_username_block_signal
from .defender_vars import get_username_from_request, REDIS_SERVER

def get_username(request, get_usernamefunc=None):
    if(get_usernamefunc is None):
        return get_username_from_request(request)
    else:
        return get_usernamefunc(request)


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
    if def_config.DISABLE_USERNAME_LOCKOUT:
        # no need to block, we disabled it.
        return
    key = get_blocked_cache_key(username)
    if def_config.COOLOFF_TIME:
        REDIS_SERVER.set(key, 'blocked', def_config.COOLOFF_TIME)
    else:
        REDIS_SERVER.set(key, 'blocked')
    send_username_block_signal(username)


def is_already_locked(request, get_usernameFunc, username):
    """Is this username already locked?"""
    if username is None:
        return False
    if def_config.DISABLE_USERNAME_LOCKOUT:
        return False
    if(get_usernameFunc is None):
        username = get_username(request)
    else:
        username = get_usernameFunc(request)

    return REDIS_SERVER.get(get_blocked_cache_key(username))


def get_attempt_cache_key(username):
    """ get the cache key by username """
    return "{0}:failed:username:{1}".format(def_config.CACHE_PREFIX,
                                            lower(username))


def get_blocked_cache_key(username):
    """ get the cache key by username """
    return "{0}:blocked:username:{1}".format(def_config.CACHE_PREFIX,
                                             lower(username))
