"""
OIDC provider settings
"""
from django.utils.translation import ugettext as _
from oidc_provider.lib.claims import ScopeClaims

def userinfo(claims, user):
    """
    Populate claims dict.
    """
    claims['name'] = user.name
    claims['email'] = user.email

    return claims


class CustomScopeClaims(ScopeClaims):

    info_Modify_Profile = (
        'Profile Modification',
        'Ability to view and modify your profile information.',
    )

    def scope_modify_profile(self):
        # self.user - Django user instance.
        # self.userinfo - Dict returned by OIDC_USERINFO function.
        # self.scopes - List of scopes requested.
        # self.client - Client requesting this claims.
        dic = {
            'modify_profile': 'True',
            'read_profile' : 'True'
        }

        return dic

    info_Read_Profile = (
        'Profile',
        'Ability to view and use your profile information',
    )

    def scope_read_profile(self):
        dic = {
            'read_profile': 'True',
        }

        return dic

