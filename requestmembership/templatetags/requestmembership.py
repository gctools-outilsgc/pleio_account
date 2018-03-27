from django import template
from ..models import RequestMembership
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()

@register.simple_tag()
def show_request_membership():
    try:
        q = RequestMembership.objects.get(id=1)
        toggle = q.display_request
        if toggle == True:
            return True
        else:
            return ''
    except RequestMembership.DoesNotExist:
        return ''
