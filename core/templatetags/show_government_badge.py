from django import template
from django.conf import settings
from emailvalidator.validator import get_email_groups

register = template.Library()

@register.simple_tag
def show_government_badge(email):
    try:
        #user is member of > 0 groups, so much be a civil servant
        return (get_email_groups(email)[1] and settings.SHOW_GOVERNMENT_BADGE)
    except (AttributeError, IndexError): 
        return False
