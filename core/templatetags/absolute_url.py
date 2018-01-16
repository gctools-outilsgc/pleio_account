from django import template
from django.conf import settings
from urllib.parse import urljoin

register = template.Library()

@register.simple_tag
def absolute_url(relative):
    return urljoin(settings.EXTERNAL_HOST, relative)
