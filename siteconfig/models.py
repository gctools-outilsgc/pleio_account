from django.db import models

from solo.models import SingletonModel

class SiteConfiguration(SingletonModel):

    activate_site_configuration = models.BooleanField(default=False)

    elgg_url = models.CharField(max_length=255, blank=True, null=True)

    freshdesk_url = models.CharField(max_length=255, blank=True, null=True)
    freshdesk_secret_key = models.CharField(max_length=255, blank=True, null=True)

    from_email = models.CharField(max_length=255, blank=True, null=True)
    email_host = models.CharField(max_length=255, blank=True, null=True)
    email_port = models.IntegerField(blank=True, null=True)
    email_user = models.CharField(max_length=255, blank=True, null=True)
    email_password = models.CharField(max_length=255, blank=True, null=True)
    email_use_tls = models.BooleanField(default=True)

    cors_origin_whitelist = models.CharField(max_length=255, blank=True, null=True)

    profile_as_service_endpoint = models.CharField(max_length=255, blank=True, null=True)

    password_reset_timeout_days = models.IntegerField(default='1')
    account_activation_days = models.IntegerField(default='7')

    send_suspicious_behaviour_warnings = models.BooleanField(default=False)

    def __unicode__(self):
        return u"Site Configuration"

    class Meta:
        verbose_name = "Site Configuration"
