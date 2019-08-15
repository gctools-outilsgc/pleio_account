from django import template
from django.conf import settings
from oidc_provider.models import Client
from django.utils.translation import gettext, gettext_lazy as _

register = template.Library()

@register.simple_tag()
def get_client_logo(name):
    client = Client.objects.get(name=name)

    if not client.logo:
        logo = False
    else:
        logo = f'{settings.MEDIA_URL}{client.logo}'

    obj = { 'logo': logo, 'url': client.website_url }

    return obj

@register.simple_tag()
def readable_scopes(scopes):
    scope_array = []
    for scope in scopes:
        if scope == "profile" or scope == "profile":
            scope_array.append(_("Display name"))
        elif scope == "email":
            scope_array.append(_("Email"))
        elif scope == "phone":
            scope_array.append(_("Phone number"))
        elif scope == "address":
            scope_array.append(_("Work address"))

    return scope_array