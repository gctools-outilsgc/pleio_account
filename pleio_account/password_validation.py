from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from pleio_account import utils

class CustomPasswordValidator(object):

    def __init__(self, numbers=1, lowercase_letters=1, uppercase_letters=1, special_characters=1):
        self.min_numbers = numbers
        self.min_lowercase_letters = lowercase_letters
        self.min_uppercase_letters = uppercase_letters
        self.min_special_characters = special_characters

    def validate(self, password, user=None):
        special_characters = "[~\!@#\$%\^&\*\(\)_\+{}\":;'\[\]]"
        errors = []
        
        if not any(char.isdigit() for char in password):
            errors.append(ValidationError(_('Password must contain at least %(min_numbers)d digit.') % {'min_numbers': self.min_numbers}))
        if not any(char.islower() for char in password):
            errors.append(ValidationError(_('Password must contain at least %(min_lowercase_letters)d lowercase letter.') % {'min_lowercase_letters': self.min_lowercase_letters}))
        if not any(char.isupper() for char in password):
            errors.append(ValidationError(_('Password must contain at least %(min_uppercase_letters)d uppercase letter.') % {'min_uppercase_letters': self.min_uppercase_letters}))
        if not any(char in special_characters for char in password):
            errors.append(ValidationError(_('Password must contain at least %(min_special_characters)d special character.') % {'min_special_characters': self.min_special_characters}))

        if errors:
            raise ValidationError(errors)
        else:
            if utils.is_user_already_locked(user):
                utils.unblock_username(user)


    def get_help_text(self):
        return "Test"
