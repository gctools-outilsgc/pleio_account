from django.contrib import admin
from core.models import User, PleioPartnerSite, PleioLegalText

# Register your models here.
admin.site.register(User)
admin.site.register(PleioPartnerSite)
admin.site.register(PleioLegalText)