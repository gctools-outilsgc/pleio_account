from django import forms
from core.forms import RegisterForm

class OccupationRegisterForm(RegisterForm):

    occupation = forms.CharField(max_length=100)
    organization = forms.CharField(max_length=100)

    class Meta(RegisterForm.Meta):
        fields = RegisterForm.Meta.fields + ('occupation', 'organization')
