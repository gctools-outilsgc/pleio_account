from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth import password_validation
from django.conf import settings
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate 
from django.contrib.auth.forms import AuthenticationForm
from two_factor.forms import AuthenticationTokenForm, TOTPDeviceForm
from two_factor.utils import totp_digits, default_device
from core.models import User
from saml.models import IdentityProvider, ExternalId
from django.forms import Form

class SetPasswordForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    error_messages = {
        'invalid_password': _("The password is invalid."),
        'password_mismatch': _("The two password fields didn't match."),
    }

    new_password1 = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'autofocus': True}))
    new_password2 = forms.CharField(strip=False, widget=forms.PasswordInput)

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

        password_validation.validate_password(self.cleaned_data.get('new_password2'))
        return new_password2


class ShowConnectionsForm(forms.ModelForm):
    class Meta:
        model = ExternalId
        fields = ('identityproviderid', 'externalid')


