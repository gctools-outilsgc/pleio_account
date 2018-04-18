from django.shortcuts import render, HttpResponseRedirect, redirect
from django.http import JsonResponse
from .forms import RequestStepOne, RequestStepTwo
from emailvalidator.validator import is_email_valid
from requestmembership.models import LimboUser
import requests
import json

from django.contrib.auth.hashers import make_password

def requestmembership_step_one(request):
    if request.method == 'POST':
        form = RequestStepOne(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            request.session['form_one_data'] = data
            return HttpResponseRedirect('/request/two/')
        else:
            return render(request, 'requestmembership_step_one.html', {'form': form})
    else:
        form = RequestStepOne()
        if 'form_one_data' in request.session:
            data = request.session['form_one_data']

            for attr, value in data.items():
                form.fields[attr].initial = value

            del request.session['form_one_data']
        elif 'form_two_data' in request.session:
            del request.session['form_two_data']

    return render(request, 'requestmembership_step_one.html', {'form': form})

def requestmembership_step_two(request):
    if 'form_one_data' not in request.session:
        return HttpResponseRedirect('/request/one/')

    if request.method == 'POST':
        form = RequestStepTwo(request.POST)
        data = request.session['form_one_data']

        if form.is_valid():
            data2 = form.cleaned_data

            limboUser = LimboUser(
                name=data2['name'],
                email=data2['email'],
                address=data2['address'],
                how=data2['reason'],
                howmore=data2['morereason'],
                website=data2['website'],
                password=make_password(data2['password2'])
            )

            limboUser.save()

            api_key = ""
            domain = ""
            password = "x"
            product_id = ""

            headers = { 'Content-Type' : 'application/json' }

            ticket = {
                'product_id': product_id,
                'subject' : data2['name'] +' ('+data2['email']+') has requested membership',
                'description' : 'Testing request membership ticket creation',
                'type': 'Other | Autres',
                'email' : '',
                'priority' : 1,
                'status' : 2,
                'source' : '9'
            }

            r = requests.post("https://"+ domain +".freshdesk.com/api/v2/tickets", auth = (api_key, password), headers = headers, data = json.dumps(ticket))

            if r.status_code == 201:
              print("Ticket created successfully, the response is given below" + r.content)
            else:
              print("Failed to create ticket, errors are displayed below,")
              response = json.loads(r.content.decode('utf-8'))
              print(response)


            del request.session['form_one_data']

            return HttpResponseRedirect('/request/complete/')
    else:
        form = RequestStepTwo()
        data = request.session['form_one_data']
        data['address'] = data['streetnumber'] + ' Apt.# ' + data['aptnumber'] + ' ' + data['street'] + ', ' + data['city'] + ' ' + data['province'] + ', ' + data['country'] + ' ' + data['postal']

    return render(request, 'requestmembership_step_two.html', {'form': form, 'data': data})

    def clean(self):
        if 'back' in self.data:
            return HttpResponseRedirect('/request/one/')

def requestmembership_complete(request):
    return render(request, 'requestmembership_complete.html')

def validate_email(request):
    email = request.GET.get('email', None)
    if not is_email_valid(email):
        data = {
            'valid': False
        }
    else:
        data = {
            'valid': True
        }

    return JsonResponse(data)
