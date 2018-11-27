from defender import config as def_config

import accountlockout.helper.ip_helper
from accountlockout.helper.users_helper import REDIS_SERVER, __get_username, __lower, __get_attempt_cache_key, \
    __get_blocked_cache_key
from . import utils

def get_from_request(request):
    """ unloads username from default POST request """
    if def_config.USERNAME_FORM_FIELD in request.POST:
        return request.POST[def_config.USERNAME_FORM_FIELD][:255]
    return None


def get_user_attempts(request, get_usernamefunc, username=None):
    """ Returns number of access attempts for this ip, username
    """
    ip_address = accountlockout.helper.ip_helper.__get(request)
    username = __lower(username or __get_username(request, get_usernamefunc))
    # get by IP
    ip_count = REDIS_SERVER.get(accountlockout.helper.ip_helper.__get_attempt_cache_key(ip_address))
    if not ip_count:
        ip_count = 1
    else:
        # we add 1 to the Redis count because the Redis index starts at 0
        ip_count = int(ip_count) + 1

    # get by username
    username_count = REDIS_SERVER.get(__get_attempt_cache_key(username))
    if not username_count:
        username_count = 1
    else:
        # we add 1 to the Redis count because the Redis index starts at 0
        username_count = int(username_count) + 1
    # return the larger of the two.
    return max(ip_count, username_count)

def get_blocked_usernames():
    """ get a list of blocked usernames from redis """
    if def_config.DISABLE_USERNAME_LOCKOUT:
        # There are no blocked usernames since we disabled them.
        return []
    key = __get_blocked_cache_key("*")
    key_list = [redis_key.decode('utf-8')
                for redis_key in REDIS_SERVER.keys(key)]
    return utils.__strip_keys(key_list)

