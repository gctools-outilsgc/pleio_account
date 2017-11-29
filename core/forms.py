from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth import password_validation
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from two_factor.forms import AuthenticationTokenForm, TOTPDeviceForm
from two_factor.utils import totp_digits
from emailvalidator.validator import is_email_valid
from .models import User


class EmailField(forms.EmailField):
    def clean(self, value):
        super(EmailField, self).clean(value)
        if not is_email_valid(value):
            raise forms.ValidationError(
                _("Your email address is not allowed.")
            )
        try:
            User.objects.get(email=value)
            raise forms.ValidationError("This e-mail is already registered.")
        except User.DoesNotExist:
            return value


class RegisterForm(forms.Form):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    name = forms.CharField(required=True, max_length=100)
    email = EmailField(required=True)
    password1 = forms.CharField(strip=False, widget=forms.PasswordInput)
    password2 = forms.CharField(strip=False, widget=forms.PasswordInput)
    accepted_terms = forms.BooleanField(required=True)
    receives_newsletter = forms.BooleanField(required=False)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

        password_validation.validate_password(self.cleaned_data.get('password2'))
        return password2


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('name', 'email', 'avatar')


class PleioAuthenticationForm(AuthenticationForm):
    is_persistent = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'is_persistent')


class PleioAuthenticationTokenForm(AuthenticationTokenForm):
    otp_token = forms.IntegerField(label=_("Token"), widget=forms.TextInput)


class PleioTOTPDeviceForm(TOTPDeviceForm):
    token = forms.IntegerField(label=_("Token"), widget=forms.TextInput)
