from django.shortcuts import render, redirect
from emailvalidator.validator import is_email_valid
from occupationfields.forms import OccupationRegisterForm
from django.utils import translation
from django.http import JsonResponse
from collections import OrderedDict
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

    result = requests.get('https://gccollab.ca/services/api/rest/json/?method=get.fields&id=0')

    field_data = json.loads(result.text)

    lang = translation.get_language()
    data = {
        'federal': json.loads(field_data['result']['federal'][lang], object_pairs_hook=OrderedDict),
        'university': json.loads(field_data['result']['academic']['university'][lang], object_pairs_hook=OrderedDict),
        'college': json.loads(field_data['result']['academic']['college'][lang], object_pairs_hook=OrderedDict),
        'ministry': json.loads(field_data['result']['provincial']['ministry'][lang], object_pairs_hook=OrderedDict),
        'other': json.loads(field_data['result']['other'][lang], object_pairs_hook=OrderedDict)
    }

    return render(request, 'occupation_fields.html', {'form': form, 'fields': data })

def validateEmail(request):
    email = request.GET.get('email', None);
    if not is_email_valid(email):
        data = { 'valid': False }
    else:
        data = { 'valid': True }
    return JsonResponse(data)
