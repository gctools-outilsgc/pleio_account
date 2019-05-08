from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import gettext, gettext_lazy as _
from django.utils import dateparse

register = template.Library()

@register.simple_tag
def include_asset(file_name):
    return mark_safe(open(settings.STATICFILES_DIRS[0]+file_name).read())

@register.simple_tag
def load_question(value):
    QUESTIONS = [
        _('Please select one of the questions'),
        _('What is your favourite board game?'),
        _('Who is your favourite fictional character?'),
        _('What is your least favourite chore?'),
        _('What type of music do you dislike most?'),
        _('What was your favourite TV show when you were a child?'),
        _('Who was your best friend in kindergarten?'),
        _('If you won the lottery, what would be your first big purchase?'),
        _('What is the first movie you saw in theatres?'),
        _('What was your first cell phone?'),
        _('What movie do you know the most quotes from?')
    ]

    return QUESTIONS[int(value)]

@register.filter
def iso_to_dateTime(value):
    return dateparse.parse_duration(value)
