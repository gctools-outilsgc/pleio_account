from django import forms
from django.utils.translation import gettext, gettext_lazy as _
from core.models import User
from core.forms import EmailField
from emailvalidator.validator import is_email_valid

class RequestStepOne(forms.Form):
    name = forms.CharField(required=True, max_length=100, widget=forms.TextInput(attrs={'aria-labelledby':"error_name"}))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'aria-labelledby':"error_email"}))

    def clean_email(self):
        # Get the emails
        email = self.cleaned_data.get('email')
        try:
            match = User.objects.get(email=email)
        except User.DoesNotExist:
            return email

        raise forms.ValidationError(self.error_messages['unique_email'], code='unique_email',)

class RequestStepTwo(forms.Form):
    name = forms.CharField(required=True, max_length=100, widget=forms.TextInput(attrs={'aria-labelledby':"error_name"}))
    email = forms.CharField(required=True, widget=forms.TextInput(attrs={'aria-labelledby':"error_email"}))
    number = forms.CharField(required=True, max_length=10)
    street = forms.CharField(required=True, max_length=100)
    city = forms.CharField(required=True, max_length=100)
    province = forms.CharField(required=True, max_length=3)
    country = forms.CharField(required=True, max_length=30)
    postal = forms.CharField(required=True, max_length=6)

    reason = forms.CharField(required=True, max_length=280, widget=forms.Textarea(attrs={'rows':4, 'cols':40}))
    website = forms.URLField(required=True)
    password1 = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'aria-labelledby':"error_password1", "aria-describedby":"password_help"}))
    password2 = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'aria-labelledby':"error_password2"}))
    accepted_terms = forms.BooleanField(required=True)
