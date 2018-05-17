from __future__ import absolute_import, unicode_literals
from celery import Celery, task

@task
def refresh_saml_idp_metadata(self):
    idps = IdentityProvider.objects.all()
    for idp in idps:
        idp.get_idp_metadata()