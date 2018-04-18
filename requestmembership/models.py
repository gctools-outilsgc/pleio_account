from django.db import models
from django.contrib import admin
from core.models import User
import json
import requests

class RequestMembership(models.Model):
    display_request = models.BooleanField(default=True)

class LimboUser(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    address = models.CharField(max_length=200)
    how = models.CharField(max_length=50)
    howmore = models.CharField(max_length=50)
    website = models.CharField(max_length=100)
    accepted_terms = models.BooleanField(default=True)
    password = models.CharField(max_length=200)

    def __str__(self):
        return '%s - %s' % (self.name, self.email)

    def create_ticket(self):
        api_key = "JulflwJWqUmcmuJaFTwu"
        domain = "cdegrass"
        password = "x"
        product_id = 2100000290

        headers = { 'Content-Type' : 'application/json' }

        ticket = {
            'product_id': product_id,
            'subject' : self.name +' ('+self.email+') has requested membership',
            'description' : 'Ticket detail',
            'type': 'Other | Autres',
            'email' : 'ethan.wallace@tbs-sct.gc.ca',
            'priority' : 1,
            'status' : 2,
            'source' : '9'
        }

        r = requests.post("https://"+ domain +".freshdesk.com/api/v2/tickets", auth = (api_key, password), headers = headers, data = json.dumps(ticket))

admin.site.register(RequestMembership)
