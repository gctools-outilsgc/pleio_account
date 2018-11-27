import logging
from django.utils.module_loading import import_string
from defender.connection import get_redis_connection
from defender import config as def_config

REDIS_SERVER = get_redis_connection()
LOG = logging.getLogger(__name__)


get_username_from_request = import_string(
    def_config.GET_USERNAME_FROM_REQUEST_PATH
)
