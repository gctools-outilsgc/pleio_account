from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render

import accountlockout.helper.ip_helper
import accountlockout.helper.users_helper
from accountlockout.helper.utils_helper import __send_blocked_email
from defender.data import store_login_attempt
from defender import config as def_config
from . import users


def is_already_locked(request, get_username=None, username=None):
    """Parse the username & IP from the request, and see if it's
    already locked."""
    user_blocked = accountlockout.helper.users_helper.__is_already_locked(request, username, get_username)
    ip_blocked = accountlockout.helper.ip_helper.__is_source_already_locked(accountlockout.helper.ip_helper.__get(request))

    if def_config.LOCKOUT_BY_IP_USERNAME:
        # if both this IP and this username are present the request is blocked
        return ip_blocked and user_blocked

    return ip_blocked or user_blocked


def get_time():
    return int(def_config.COOLOFF_TIME / 60);


def get_attemps_left(request):
    return (def_config.FAILURE_LIMIT - users.get_user_attempts(request));

def lockout_response(request):
    """ if we are locked out, here is the response """
    username = accountlockout.helper.users_helper.get_username_from_request(request)
    if def_config.LOCKOUT_TEMPLATE:
        context = {
            'cooloff_time_seconds': def_config.COOLOFF_TIME,
            'cooloff_time_minutes': int(def_config.COOLOFF_TIME / 60),
            'failure_limit': def_config.FAILURE_LIMIT,
            'email_lockout': username,
        }
        __send_blocked_email(request, username)
        return render(request, def_config.LOCKOUT_TEMPLATE, context)

    if def_config.LOCKOUT_URL:
        return HttpResponseRedirect(def_config.LOCKOUT_URL)

    if def_config.COOLOFF_TIME:
        return HttpResponse("Account locked: too many login attempts.  "
                            "Please try again later.")
    else:
        return HttpResponse("Account locked: too many login attempts.  "
                            "Contact an admin to unlock your account.")

def add_login_attempt_to_db(request, login_valid,get_usernamefunc=None,username=None):
    """ Create a record for the login attempt If using celery call celery
    task, if not, call the method normally """

    if not def_config.STORE_ACCESS_ATTEMPTS:
        # If we don't want to store in the database, then don't proceed.
        return

    username = username or accountlockout.helper.users_helper.__get_username(request, get_usernamefunc)

    user_agent = request.META.get('HTTP_USER_AGENT', '<unknown>')[:255]
    ip_address = accountlockout.helper.ip_helper.__get(request)
    http_accept = request.META.get('HTTP_ACCEPT', '<unknown>')
    path_info = request.META.get('PATH_INFO', '<unknown>')

    if def_config.USE_CELERY:
        from .tasks import add_login_attempt_task
        add_login_attempt_task.delay(user_agent, ip_address, username,
                                     http_accept, path_info, login_valid)
    else:
        store_login_attempt(user_agent, ip_address, username, http_accept, path_info, login_valid)

