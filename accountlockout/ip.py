from defender import config as def_config
from accountlockout.helper.ip_helper import REDIS_SERVER, get_blocked_cache_key
from .helper import utils_helper


def get_blocked_ips():
    """ get a list of blocked ips from redis """
    if def_config.DISABLE_IP_LOCKOUT:
        # There are no blocked IP's since we disabled them.
        return []
    key = get_blocked_cache_key("*")
    key_list = [redis_key.decode('utf-8')
                for redis_key in REDIS_SERVER.keys(key)]
    return utils_helper.strip_keys(key_list)