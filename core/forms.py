import requests
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import password_validation
from django.conf import settings
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template import loader
from django.views.generic.edit import FormView
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from two_factor.forms import AuthenticationTokenForm, TOTPDeviceForm
from emailvalidator.validator import is_email_valid

from .models import User, SiteConfiguration
from .helpers import verify_captcha_response

SUBJECT_TEMPLATE_NAME = 'emails/reset_password_subject.txt'
EMAIL_TEMPLATE_NAME = 'emails/reset_password.txt'
HTML_EMAIL_TEMPLATE_NAME = 'emails/reset_password.html'


class PasswordResetRequestForm(forms.Form):
    email = forms.CharField(label=("Email address"), max_length=254)


class ResetPasswordRequestView(FormView):
    template_name = 'password_reset.html'
    success_url = '/password_reset/done/'
    form_class = PasswordResetRequestForm

    @staticmethod
    def validate_email_address(email):
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        # Load site configuration
        site_config = SiteConfiguration.objects.get()
        config_data = site_config.get_values()

        if form.is_valid():
            email = form.cleaned_data["email"]

        if not self.validate_email_address(email):
            form.add_error(None, _(
                'Please check your email for instructions on how to reset '
                'your password.'
            ))
            return self.form_invalid(form)

        user = User.objects.filter(email__iexact=email).get()
        if not user and config_data['elgg_url']:
            elgg_url = config_data['elgg_url']

            # Verify user exists in Elgg
            user_exists = requests.post(
                elgg_url + '/services/api/rest/json/',
                data={
                    'method': 'pleio.userexists',
                    'user': email
                }
            ).json()
            name = user_exists.get('result', {}).get('name', email)
            valid_user = user_exists.get('result', {}).get('valid', False)

            if not valid_user:
                form.add_error(None, _(
                    'Please check your email for instructions on how to reset '
                    'your password.'
                ))
                return self.form_invalid(form)

            # If exists in Elgg, create local user
            user = User.objects.create_user(
                name=name,
                email=email,
                accepted_terms=True,
                receives_newsletter=True
            )
            user.is_active = True
            user.save()
        elif not user:
            form.add_error(None, _(
                'Please check your email for instructions on how to reset '
                'your password.'
            ))
            return self.form_invalid(form)

        # Variables passed into the rendered template.
        template_context = {
            'domain': request.META['HTTP_HOST'],
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': user,
            'token': default_token_generator.make_token(user),
            'protocol': request.is_secure() and "https" or "http"
        }

        send_mail(
            ''.join(loader.render_to_string(
                SUBJECT_TEMPLATE_NAME,
                template_context
            ).splitlines()),
            loader.render_to_string(EMAIL_TEMPLATE_NAME, template_context),
            config_data['from_email'],
            [user.email],
            fail_silently=False,
            html_message=loader.render_to_string(
                HTML_EMAIL_TEMPLATE_NAME,
                template_context
            )
        )

        return self.form_valid(form)


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

    name = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={
            'aria-labelledby': 'error_name'
        })
    )
    email = EmailField(
        required=True,
        widget=forms.TextInput(attrs={
            'aria-labelledby': 'error_email'
        })
    )
    password1 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={
            'aria-labelledby': 'error_password1'
        })
    )
    password2 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={
            'aria-labelledby': 'error_password2'
        })
    )
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
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email

        raise forms.ValidationError(
            self.error_messages['unique_email'],
            code='unique_email',
        )

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        password_validation.validate_password(password1)
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

        return password2

    def clean(self):
        super().clean()
        recaptcha = self.cleaned_data.get('g-recaptcha-response')
        if not verify_captcha_response(recaptcha):
            raise forms.ValidationError(
                self.error_messages['captcha_mismatch'],
                code='captcha_mismatch',
            )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('name', 'email', 'receives_newsletter',)


class LabelledLoginForm(AuthenticationForm):
        username = forms.CharField(
            required=True,
            max_length=254,
            widget=forms.TextInput(attrs={
                'id': 'id_auth-username',
                'aria-labelledby': 'error_login'
            })
        )
        password = forms.CharField(
            required=True,
            strip=False,
            widget=forms.PasswordInput(attrs={
                'autocomplete': 'off'
            })
        )


class PleioAuthenticationForm(AuthenticationForm):
    error_messages = {
        'captcha_mismatch': 'captcha_mismatch',
    }

    username = forms.CharField(
        required=True,
        max_length=254,
        widget=forms.TextInput(attrs={
            'id': 'id_auth-username',
            'aria-labelledby': 'error_login'
        })
    )

    def __init__(self, *args, **kwargs):
        super(PleioAuthenticationForm, self).__init__(*args, **kwargs)

        if getattr(settings, "GOOGLE_RECAPTCHA_SITE_KEY", None):
            self.fields['g-recaptcha-response'] = forms.CharField()

    def clean(self):
        super().clean()
        recaptcha = self.cleaned_data.get('g-recaptcha-response')
        if not verify_captcha_response(recaptcha):
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

    old_password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={
            'aria-labelledby': "error_id_old_password"
        })
    )
    new_password1 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={
            'aria-labelledby': "error_id_new_password1"
        })
    )
    new_password2 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={
            'aria-labelledby': "error_id_new_password2"
        })
    )

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

        password_validation.validate_password(
            self.cleaned_data.get('new_password2')
        )

        return new_password2
