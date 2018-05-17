from django.db.models.signals import post_save
from django.dispatch import receiver

from saml.models import IdentityProvider

@receiver(post_save, sender=IdentityProvider)
def renew_idp_metadata(sender, instance, created, update_fields=None, **kwargs):
    '''
    When the model is created (created=True) or modified at the admin panel (update_fields=None)
    the fields provided by the IdentityProvider will be collected
    '''
    if created or not update_fields:
        instance.get_idp_metadata()
