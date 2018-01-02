from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()
 
@register.simple_tag
def include_asset(file_name):
    return mark_safe(open(settings.STATICFILES_DIRS[0]+file_name).read())