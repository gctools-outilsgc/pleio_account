import requests
import json
from .models import User
from django.core.mail.backends.smtp import EmailBackend
from constance import config


class ElggBackend:
    def authenticate(self, request, username=None, password=None):
        if not config.ELGG_URL:
            return

        # Check if user exists (case-insensitive)
        try:
            user = User.objects.get(email__iexact=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            # Verify username/password combination
            valid_user_request = requests.post(
                config.ELGG_URL + "/services/api/rest/json/",
                data={
                    'method': 'pleio.verifyuser',
                    'user': username,
                    'password': password
                }
            )
            valid_user_json = json.loads(valid_user_request.text)
            valid_user_result = valid_user_json["result"] if 'result' in valid_user_json else []
            valid_user = valid_user_result["valid"] if 'valid' in valid_user_result else False
            name = valid_user_result["name"] if 'name' in valid_user_result else username
            admin = valid_user_result["admin"] if 'admin' in valid_user_result else False

            # If valid, create new user with Elgg attributes
            if valid_user is True:
                user = User.objects.create_user(
                    name=name,
                    email=username.lower(),
                    password=password,
                    accepted_terms=True,
                    receives_newsletter=True
                )
                user.is_active = True
                user.is_admin = admin
                user.save()
                return user
            else:
                return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class SiteConfigEmailBackend(EmailBackend):
    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=None, use_ssl=None, timeout=None,
                 ssl_keyfile=None, ssl_certfile=None,
                 **kwargs):

        super(SiteConfigEmailBackend, self).__init__(
             host=host or config.EMAIL_HOST,
             port=port or config.EMAIL_PORT,
             username=username or config.EMAIL_USER,
             password=password or config.EMAIL_PASS,
             use_tls=use_tls or config.EMAIL_SECURITY == 'tls',
             use_ssl=use_ssl or config.EMAIL_SECURITY == 'ssl',
             fail_silently=fail_silently or config.EMAIL_FAIL_SILENTLY,
             timeout=timeout or config.EMAIL_TIMEOUT,
             ssl_keyfile=ssl_keyfile,
             ssl_certfile=ssl_certfile,
             **kwargs
        )

    #def send_messages(self, email_messages):
    #    return len(list(email_messages))

__all__ = ['SiteConfigEmailBackend']