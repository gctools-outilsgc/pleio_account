from django import template
from django.conf import settings

register = template.Library()
 
@register.simple_tag
def include_asset(file_name):
    return open(settings.STATICFILES_DIRS[0]+file_name).read()