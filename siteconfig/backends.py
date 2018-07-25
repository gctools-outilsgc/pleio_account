from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend

class SiteConfigEmailBackend(EmailBackend):
    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=None, use_ssl=None, timeout=None,
                 ssl_keyfile=None, ssl_certfile=None,
                 **kwargs):

        from siteconfig.models import SiteConfiguration
        configuration = SiteConfiguration.objects.get()

        super(SiteConfigEmailBackend, self).__init__(
             host = configuration.email_host if host is None else host,
             port = configuration.email_port if port is None else port,
             username = configuration.email_user if username is None else username,
             password = configuration.email_password if password is None else password,
             use_tls = configuration.email_use_tls if use_tls is None else use_tls,
             fail_silently = fail_silently,
             use_ssl = use_ssl,
             timeout = timeout,
             ssl_keyfile = ssl_keyfile,
             ssl_certfile = ssl_certfile,
             **kwargs)


__all__ = ['SiteConfigEmailBackend']
