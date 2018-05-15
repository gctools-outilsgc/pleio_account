from django.utils.translation import gettext, gettext_lazy as _
from django import template
from django.http import JsonResponse
import requests
import json

register = template.Library()

@register.simple_tag()
def get_occupation_info():
    r = requests.get('https://dev.gccollab.ca/services/api/rest/json/?method=get.fields&id=0')
    return r.json()

@register.simple_tag()
def get_user_types():
    types = (
        ('none', '...'),
        ('academic', _('Academic')),
        ('student', _('Student')),
        ('federal', _('Federal Government')),
        ('provincial', _('Provincial/Territorial Government')),
        ('municipal', _('Municipal Government')),
        ('international', _('International/Foreign Government')),
        ('ngo', _('Non-Governmental Organization')),
        ('community', _('Community/Non-profit')),
        ('business', _('Business')),
        ('media', _('Media')),
        ('retired', _('Retired Public Servant')),
        ('other', _('Other'))
    )

    return types

@register.simple_tag()
def get_provinces():
    provinces = (
        ('none', '...'),
        ('Alberta', _('Alberta')),
        ('British Columbia', _('British Columbia')),
        ('Manitoba', _('Manitoba')),
        ('New Brunswick', _('New Brunswick')),
        ('Newfoundland and Labrador', _('Newfoundland and Labrador')),
        ('Nova Scotia', _('Nova Scotia')),
        ('Nunavut', _('Nunavut')),
        ('Ontario', _('Ontario')),
        ('Prince Edward Island', _('Prince Edward Island')),
        ('Quebec', _('Quebec')),
        ('Saskatchewan', _('Saskatchewan')),
        ('Yukon', _('Yukon'))
    )

    return provinces
