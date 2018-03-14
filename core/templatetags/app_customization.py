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

@register.simple_tag()
def show_language_toggle():
    try:
        q = AppCustomization.objects.get(id=1)
        toggle = q.display_language_toggle
        if toggle == True:
            return True
        else:
            return ''
    except AppCustomization.DoesNotExist:
        return ''

@register.simple_tag()
def custom_helpdesk_link():
    try:
        q = AppCustomization.objects.get(id=1)
        return q.custom_helpdesk_link
    except AppCustomization.DoesNotExist:
        return ''

@register.simple_tag()
def show_footer_images():
    try:
        q = AppCustomization.objects.get(id=1)
        if q.footer_image_left and q.footer_image_right:
            return True
        else:
            return False
    except AppCustomization.DoesNotExist:
        return ''

@register.simple_tag()
def show_footer_image_left():
    try:
        q = AppCustomization.objects.get(id=1)
        if not q.footer_image_left:
            return ''
        else:
            return q.footer_image_left.url
    except AppCustomization.DoesNotExist:
        return ''

@register.simple_tag()
def show_footer_image_right():
    try:
        q = AppCustomization.objects.get(id=1)
        if not q.footer_image_right:
            return ''
        else:
            return q.footer_image_right.url
    except AppCustomization.DoesNotExist:
        return ''
