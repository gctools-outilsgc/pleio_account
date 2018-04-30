from django import template
from core.models import PleioPartnerSite
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()

@register.inclusion_tag('partner_links.html')
def partner_links():
    try:
        partners = PleioPartnerSite.objects.all()
        return {'partners':partners}
    except PleioPartnerSite.DoesNotExist:
        return ''        