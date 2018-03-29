"""
OIDC provider settings
"""

from django.utils.translation import ugettext_lazy as _
from oidc_provider.lib.claims import ScopeClaims

def userinfo(claims, user):
    """
    Populate claims dict.
    """
    claims['name'] = user.name
    claims['email'] = user.email

    return claims

class CustomScopeClaims(ScopeClaims):
    """
    Change description of profile scope.
    """
    info_profile = (
        _('Basic profile'),
        _('Access to your name'),
    )
