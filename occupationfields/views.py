from django.shortcuts import render, redirect
from occupationfields.forms import OccupationRegisterForm
from django.utils import translation
import requests
import json

def registerOccupation(request):
    if request.user.is_authenticated():
        return redirect('profile')

    if request.method == "POST":
        form = OccupationRegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                user = User.objects.create_user(
                    name=data['name'],
                    email=data['email'],
                    password=data['password2'],
                    accepted_terms=data['accepted_terms']
                )
            except:
                user = User.objects.get(email=data['email'])

            if not user.is_active:
                user.send_activation_token(request)

            return redirect('register_complete')
    else:
        form = OccupationRegisterForm()

    result = requests.get('https://dev.gccollab.ca/services/api/rest/json/?method=get.fields&id=0')

    field_data = json.loads(result.text)

    lang = translation.get_language()

    return render(request, 'occupation_fields.html', {'form': form, 'fields': json.loads(field_data['result']['federal'][lang])})

def verifyEmail(request):

    return True
