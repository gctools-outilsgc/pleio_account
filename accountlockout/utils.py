import logging
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.mail import send_mail
from django.template import loader
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

import accountlockout.helper.ip_helper
from core.models import User, SiteConfiguration
from defender.connection import get_redis_connection
from defender.data import store_login_attempt
from defender import config as def_config
from . import ip, users

LOG = logging.getLogger(__name__)

REDIS_SERVER = get_redis_connection()

def is_already_locked(request, get_username=None, username=None):
    """Parse the username & IP from the request, and see if it's
    already locked."""
    user_blocked = users.__is_already_locked(request, username, get_username)
    ip_blocked = accountlockout.helper.ip_helper.__is_source_already_locked(accountlockout.helper.ip_helper.__get(request))

    if def_config.LOCKOUT_BY_IP_USERNAME:
        # if both this IP and this username are present the request is blocked
        return ip_blocked and user_blocked

    return ip_blocked or user_blocked

def __strip_keys(key_list):
    """ Given a list of keys, remove the prefix and remove just
    the data we care about.

    for example:

        ['defender:blocked:ip:ken', 'defender:blocked:ip:joffrey']

    would result in:

        ['ken', 'joffrey']

    """
    return [key.split(":")[-1] for key in key_list]

def get_time():
    return int(def_config.COOLOFF_TIME / 60);

def __increment_key(key):
    """ given a key increment the value """
    pipe = REDIS_SERVER.pipeline()
    pipe.incr(key, 1)
    if def_config.COOLOFF_TIME:
        pipe.expire(key, def_config.COOLOFF_TIME)
    new_value = pipe.execute()[0]
    return new_value

def get_attemps_left(request):
    return (def_config.FAILURE_LIMIT - users.get_user_attempts(request));

def lockout_response(request):
    """ if we are locked out, here is the response """
    username = users.get_username_from_request(request)
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

    username = username or users.get_username(request, get_usernamefunc)

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

def __send_blocked_email(request, username):
    if __validate_email_address(username):
        found_user = User.objects.filter(email__iexact=username)
        if found_user.exists():
            #load site configuration
            site_config = SiteConfiguration.get_solo()
            config_data = site_config.get_values()
            for user in found_user:

                c = {
                    'domain': request.META['HTTP_HOST'],
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'user': user,
                    'token': default_token_generator.make_token(user),
                    'protocol': request.is_secure() and "https" or "http",
                    'attemps': def_config.IP_FAILURE_LIMIT,
                    'time': int(def_config.COOLOFF_TIME /60)
                }

                subject_template_name = 'emails/reset_password_subject.txt'
                email_template_name = 'emails/reset_password.txt'
                html_email_template_name = 'emails/reset_password_lockout.html'
                subject = loader.render_to_string(subject_template_name)
                subject = ''.join(subject.splitlines())
                email = loader.render_to_string(email_template_name, c)
                html_email = loader.render_to_string(html_email_template_name, c)
                send_mail(subject, email, config_data['from_email'], [user.email], fail_silently=False, html_message=html_email)

def __validate_email_address(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False