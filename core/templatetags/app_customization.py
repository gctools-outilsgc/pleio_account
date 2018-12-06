from django import template
from django.conf import settings
from constance import config

register = template.Library()


@register.simple_tag()
def show_customizations_title():
    return config.APP_TITLE


@register.simple_tag()
def show_customizations_color():
    color = config.APP_BRAND_COLOR
    return color[1:] if color.startswith('#') else color


@register.simple_tag()
def show_customizations_logo():
    if config.APP_LOGO:
        return settings.MEDIA_URL + config.APP_LOGO
    return ''


@register.simple_tag()
def show_customizations_bg_image():
    bg_image = config.APP_BACKGROUND_IMAGE
    if not bg_image:
        return ' none;'

    return f'url({settings.MEDIA_URL}{bg_image}); ' + {
            'T': 'background-repeat: repeat;',
            'C': 'background-repeat: no-repeat; background-size: cover;'
    }[config.APP_BACKGROUND_OPTIONS]


@register.simple_tag()
def show_customizations_favicon():
    if config.APP_FAVICON:
        return settings.MEDIA_URL + config.APP_FAVICON
    return ''


@register.simple_tag()
def show_language_toggle():
    return config.APP_LANGUAGE_TOGGLE


@register.simple_tag()
def email_language_toggle():
    return config.APP_USE_ALL_LANGUAGES_IN_EMAIL


@register.simple_tag()
def custom_helpdesk_link():
    return config.APP_HELPDESK_LINK


@register.simple_tag()
def show_footer_images():
    return config.APP_FOOTER_IMAGE_LEFT and config.APP_FOOTER_IMAGE_RIGHT


@register.simple_tag()
def show_footer_image_left():
    if config.APP_FOOTER_IMAGE_LEFT:
        return settings.MEDIA_URL + config.APP_FOOTER_IMAGE_LEFT
    return ''


@register.simple_tag()
def show_footer_image_right():
    if config.APP_FOOTER_IMAGE_RIGHT:
        return settings.MEDIA_URL + config.APP_FOOTER_IMAGE_RIGHT
    return ''
