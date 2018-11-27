import logging

from defender import config as def_config
from defender.connection import get_redis_connection
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from core.models import User, SiteConfiguration

LOG = logging.getLogger(__name__)
REDIS_SERVER = get_redis_connection()


def strip_keys(key_list):
    """ Given a list of keys, remove the prefix and remove just
    the data we care about.

    for example:

        ['defender:blocked:ip:ken', 'defender:blocked:ip:joffrey']

    would result in:

        ['ken', 'joffrey']

    """
    return [key.split(":")[-1] for key in key_list]


def increment_key(key):
    """ given a key increment the value """
    pipe = REDIS_SERVER.pipeline()
    pipe.incr(key, 1)
    if def_config.COOLOFF_TIME:
        pipe.expire(key, def_config.COOLOFF_TIME)
    new_value = pipe.execute()[0]
    return new_value


def send_blocked_email(request, username):
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