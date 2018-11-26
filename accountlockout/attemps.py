from defender import config as def_config
from defender.connection import get_redis_connection
from . import ip,users,utils

REDIS_SERVER = get_redis_connection()

def reset_failed(ip_address=None, username=None):
    """ reset the failed attempts for these ip's and usernames
    """
    pipe = REDIS_SERVER.pipeline()

    ip.unblock(ip_address, pipe=pipe)
    users.unblock(username, pipe=pipe)

    pipe.execute()

def record_failed(request,ip_address, username):
    """ record the failed login attempt, if over limit return False,
    if not over limit return True """
    # increment the failed count, and get current number
    ip_block = False

    if not def_config.DISABLE_IP_LOCKOUT:
        # we only want to increment the IP if this is disabled.
        ip_count = utils.increment_key(ip.get_attempt_cache_key(ip_address)) + 1
            # if over the limit, add to block
        if ip_count > def_config.IP_FAILURE_LIMIT:
            ip.block(ip_address)
            ip_block = True

    user_block = False
    if username and not def_config.DISABLE_USERNAME_LOCKOUT:
        user_count = utils.increment_key(users.get_attempt_cache_key(username)) + 1
        # if over the limit, add to block
        if user_count > def_config.USERNAME_FAILURE_LIMIT:
            users.block(username)
            user_block = True

    # if we have this turned on, then there is no reason to look at ip_block
    # we will just look at user_block, and short circut the result since
    # we don't need to continue.
    if def_config.DISABLE_IP_LOCKOUT:
        # if user_block is True, it means it was blocked
        # we need to return False
        return not user_block

    if def_config.DISABLE_USERNAME_LOCKOUT:
        # The same as DISABLE_IP_LOCKOUT
        return not ip_block

    # we want to make sure both the IP and user is blocked before we
    # return False
    # this is mostly used when a lot of your users are using proxies,
    # and you don't want one user to block everyone on that one IP.
    if def_config.LOCKOUT_BY_IP_USERNAME:
        # both ip_block and user_block need to be True in order
        # to return a False.
        return not (ip_block and user_block)

    # if any blocks return False, no blocks. return True
    return not (ip_block or user_block)