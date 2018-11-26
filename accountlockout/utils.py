from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from defender.connection import get_redis_connection
from defender.data import store_login_attempt
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

def lockout_response(request):
    """ if we are locked out, here is the response """
    username = users.get_username_from_request(request)
    if config.LOCKOUT_TEMPLATE:
        context = {
            'cooloff_time_seconds': config.COOLOFF_TIME,
            'cooloff_time_minutes': int(config.COOLOFF_TIME / 60),
            'failure_limit': config.FAILURE_LIMIT,
            'email_lockout': username,
        }
        #send_blocked_email(request, username)
        return render(request, config.LOCKOUT_TEMPLATE, context)

    if config.LOCKOUT_URL:
        return HttpResponseRedirect(config.LOCKOUT_URL)

    if config.COOLOFF_TIME:
        return HttpResponse("Account locked: too many login attempts.  "
                            "Please try again later.")
    else:
        return HttpResponse("Account locked: too many login attempts.  "
                            "Contact an admin to unlock your account.")

def add_login_attempt_to_db(request, login_valid,
                            get_username=users.get_username_from_request,
                            username=None):
    """ Create a record for the login attempt If using celery call celery
    task, if not, call the method normally """

    if not config.STORE_ACCESS_ATTEMPTS:
        # If we don't want to store in the database, then don't proceed.
        return

    username = username or get_username(request)

    user_agent = request.META.get('HTTP_USER_AGENT', '<unknown>')[:255]
    ip_address = ip.get(request)
    http_accept = request.META.get('HTTP_ACCEPT', '<unknown>')
    path_info = request.META.get('PATH_INFO', '<unknown>')

    if config.USE_CELERY:
        from .tasks import add_login_attempt_task
        add_login_attempt_task.delay(user_agent, ip_address, username,
                                     http_accept, path_info, login_valid)
    else:
        store_login_attempt(user_agent, ip_address, username, http_accept, path_info, login_valid)