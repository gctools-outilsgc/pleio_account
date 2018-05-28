from django import forms
from core.forms import RegisterForm, EmailField

class OccupationRegisterForm(RegisterForm):

    occupation = forms.CharField(max_length=100)
    organization = forms.CharField(max_length=100)
    email = EmailField(required=True, widget=forms.TextInput(attrs={'aria-labelledby':"error_email", 'onfocusout': "validateEmail(this)"}))

    class Meta(RegisterForm.Meta):
        fields = RegisterForm.Meta.fields + ('occupation', 'organization')
