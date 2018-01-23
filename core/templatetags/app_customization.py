from django import template
from core.models import AppCustomization
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()

@register.simple_tag()
def show_customizations_title():
    try:
        q = AppCustomization.objects.get(id=1)
        return q.product_title
    except AppCustomization.DoesNotExist:
        return ''

@register.simple_tag()
def show_customizations_color():
    try:
        q = AppCustomization.objects.get(id=1)
        return q.color_hex
    except AppCustomization.DoesNotExist:
        return '2185d0'

@register.simple_tag()
def show_customizations_logo():
    try:
        q = AppCustomization.objects.get(id=1)
        if not q.logo_image:
            return ''
        else:
            return q.logo_image.url
    except AppCustomization.DoesNotExist:
        return ''

@register.simple_tag()
def show_customizations_bg_image():
    try:
        q = AppCustomization.objects.get(id=1)
        if not q.app_background_photo:
            return ' none;'   
        else:
            image = q.app_background_photo.url
            option = q.app_background_options
            if option == 'T':
                return 'url(' +image+ '); background-repeat: repeat;'
            else:        
                return 'url(' +image+ '); background-repeat: no-repeat; background-size: cover;'                                     
    except AppCustomization.DoesNotExist:
        return ' none;'

@register.simple_tag()
def show_customizations_favicon():
    try:
        q = AppCustomization.objects.get(id=1)
        if not q.app_favicon:
            return ''
        else:
            return q.app_favicon.url
    except AppCustomization.DoesNotExist:
        return ''                