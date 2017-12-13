"""
Initialize the emailvalidator django application, and configure
"""
import re
from .models import EmailRegExValidator


def is_email_valid(email):
    """
    Determines if the provided email is valid based on the regular expressions
    stored in the database.
    """
    validators = EmailRegExValidator.objects.all()
    regexes = [re.compile(r.regex) for r in validators]
    return any(regex.match(email) for regex in regexes)
