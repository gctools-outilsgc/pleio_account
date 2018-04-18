from django import forms
from django.utils.translation import gettext, gettext_lazy as _
from core.models import User
from core.forms import EmailField
from emailvalidator.validator import is_email_valid
from django.core.validators import RegexValidator
from django.contrib.auth import password_validation

class RequestStepOne(forms.Form):
    name = forms.CharField(required=True, max_length=100, widget=forms.TextInput(attrs={'aria-labelledby':"error_name"}))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'aria-labelledby':"error_email"}))
    streetnumber = forms.CharField(required=True, max_length=10, validators=[RegexValidator(r'^\d{1,10}$')])
    aptnumber = forms.CharField(required=False, max_length=10, validators=[RegexValidator(r'^\d{1,10}$')])
    street = forms.CharField(required=True, max_length=100)
    city = forms.CharField(required=True, max_length=100)
    province = forms.CharField(required=True, max_length=3)
    country = forms.CharField(required=True, max_length=30)
    postal = forms.CharField(required=True, max_length=6)

    address = forms.CharField(max_length=200, required=False)

    def clean_email(self):
        # Get the emails
        email = self.cleaned_data.get('email')
        try:
            match = User.objects.get(email=email)
        except User.DoesNotExist:
            return email

        raise forms.ValidationError(self.error_messages['unique_email'], code='unique_email',)

class RequestStepTwo(forms.Form):
    REASONS = (
        ('other', _('Other')),
    )

    name = forms.CharField(required=True,widget=forms.HiddenInput())
    email = forms.CharField(required=True, widget=forms.HiddenInput())
    address = forms.CharField(required=True, widget=forms.HiddenInput())

    reason = forms.ChoiceField(choices=REASONS, required=True)
    morereason = forms.CharField(max_length=100, required=False)
    website = forms.URLField(required=False)
    password1 = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'aria-labelledby':"error_password1", "aria-describedby":"password_help"}))
    password2 = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'aria-labelledby':"error_password2"}))
    accepted_terms = forms.BooleanField(required=True)

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
