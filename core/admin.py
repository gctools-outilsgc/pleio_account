from django.contrib import admin

from solo.admin import SingletonModelAdmin
from core.models import SiteConfiguration

class OrganizeFields(SingletonModelAdmin):
        fieldsets = (
            ('', {
                'fields': ('activate_site_configuration', )
            }),
            ('Email configuration', {
                'fields': ('from_email', 'email_host', 'email_port', 'email_user', 'email_password', 'email_use_tls', 'email_use_ssl', 'email_fail_silently', 'email_timeout', 'send_suspicious_behaviour_warnings'),
            }),
            ('Timeout values', {
                'fields': ('password_reset_timeout_days', 'account_activation_days')
            }),
            ('Connection URLs', {
                'fields': ('elgg_url', 'profile_as_service_endpoint', 'cors_origin_whitelist')
            }),
            ('Freshdesk', {
                'fields': ('freshdesk_url', 'freshdesk_secret_key')
            }),
        )

admin.site.register(SiteConfiguration, OrganizeFields)
