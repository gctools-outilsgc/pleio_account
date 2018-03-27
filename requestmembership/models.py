from django.db import models
from django.contrib import admin

class RequestMembership(models.Model):
    display_request = models.BooleanField(default=True)

admin.site.register(RequestMembership)
