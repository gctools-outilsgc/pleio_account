from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth import password_validation
from django.conf import settings
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from two_factor.forms import AuthenticationTokenForm, TOTPDeviceForm
from two_factor.utils import totp_digits
from emailvalidator.validator import is_email_valid
from .models import User
from .helpers import verify_captcha_response

class EmailField(forms.EmailField):
    def clean(self, value):
        super(EmailField, self).clean(value)
        if not is_email_valid(value):
            raise forms.ValidationError(
                _("Your email address is not allowed.")
            )

        found_user = User.objects.filter(email__iexact=value, is_active=True)
        if found_user.exists():
            raise forms.ValidationError(_("This email is already registered."))
        else:
            return value


class RegisterForm(forms.Form):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'captcha_mismatch': 'captcha_mismatch',
        'unique_email': _('This email is already in use.'),
    }

    name = forms.CharField(required=True, max_length=100, widget=forms.TextInput(attrs={'aria-labelledby':"error_name"}))
    email = EmailField(required=True, widget=forms.TextInput(attrs={'aria-labelledby':"error_email"}))
    password1 = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'aria-labelledby':"error_password1"}))
    password2 = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'aria-labelledby':"error_password2"}))
    accepted_terms = forms.BooleanField(required=True)
    receives_newsletter = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        if getattr(settings, "GOOGLE_RECAPTCHA_SITE_KEY", None):
            self.fields["g-recaptcha-response"] = forms.CharField()

    def clean_email(self):
        # Get the emails
        email = self.cleaned_data.get('email')

        try:
            match = User.objects.get(email=email)
        except User.DoesNotExist:
            return email

        raise forms.ValidationError(self.error_messages['unique_email'], code='unique_email',)

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")

        password_validation.validate_password(self.cleaned_data.get('password1'))
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

        #password_validation.validate_password(self.cleaned_data.get('password2'))
        return password2

    def clean(self):
        super(RegisterForm, self).clean()
        if not verify_captcha_response(self.cleaned_data.get('g-recaptcha-response')):
            raise forms.ValidationError(
                self.error_messages['captcha_mismatch'],
                code='captcha_mismatch',
            )

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('name', 'email', 'receives_newsletter',)

class LabelledLoginForm(AuthenticationForm):
        username = forms.CharField(required=True, max_length=254, widget=forms.TextInput(attrs={'id':"id_auth-username", 'aria-labelledby':"error_login"}))

class PleioAuthenticationForm(AuthenticationForm):
    error_messages = {
        'captcha_mismatch': 'captcha_mismatch',
    }

    username = forms.CharField(required=True, max_length=254, widget=forms.TextInput(attrs={'id':"id_auth-username", 'aria-labelledby':"error_login"}))

    def __init__(self, *args, **kwargs):
        super(PleioAuthenticationForm, self).__init__(*args, **kwargs)

        if getattr(settings, "GOOGLE_RECAPTCHA_SITE_KEY", None):
            self.fields['g-recaptcha-response'] = forms.CharField()

    def clean(self):
        super(PleioAuthenticationForm, self).clean()
        if not verify_captcha_response(self.cleaned_data.get('g-recaptcha-response')):
            raise forms.ValidationError(
                self.error_messages['captcha_mismatch'],
                code='captcha_mismatch',
            )

class PleioAuthenticationTokenForm(AuthenticationTokenForm):
    otp_token = forms.IntegerField(label=_("Token"), widget=forms.TextInput)


class PleioTOTPDeviceForm(TOTPDeviceForm):
    token = forms.IntegerField(label=_("Token"), widget=forms.TextInput)


class ChangePasswordForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    error_messages = {
        'invalid_password': _("The password is invalid."),
        'password_mismatch': _("The two password fields didn't match."),
    }

    old_password = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'aria-labelledby':"error_id_old_password"}))
    new_password1 = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'aria-labelledby':"error_id_new_password1"}))
    new_password2 = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'aria-labelledby':"error_id_new_password2"}))

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        user = authenticate(username=self.user.email, password=old_password)

        if user is None:
            raise forms.ValidationError(
                self.error_messages['invalid_password'],
                code='invalid_password',
            )

        return old_password

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
