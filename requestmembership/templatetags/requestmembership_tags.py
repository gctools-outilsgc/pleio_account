from django import template
from ..models import RequestMembership
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()

@register.simple_tag()
def show_request_membership():
    try:
        q = RequestMembership.objects.all()[:1].get()
        toggle = q.display_request
        if toggle == True:
            return True
        else:
            return False
    except RequestMembership.DoesNotExist:
        return 'shit'

def show_something():
    return True
