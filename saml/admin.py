from django.contrib import admin
from saml.models import IdentityProvider, IdpEmailDomain

# Register your models here.


class IdentityProviderAdmin(admin.ModelAdmin):
    fields = ['shortname' ,
              'displayname' ,
              'metadata_url' ,
              'metadata_filename' ,
              'perform_slo' 
            ]

admin.site.register(IdentityProvider, IdentityProviderAdmin)


class IdpEmailDomainAdmin(admin.ModelAdmin):
    list_display = ('email_domain', 'identityprovider')

admin.site.register(IdpEmailDomain, IdpEmailDomainAdmin)



