"""
OIDC provider settings
"""
from django.utils.translation import ugettext as _
from oidc_provider.lib.claims import ScopeClaims
import requests
from django.conf import settings

def userinfo(claims, user):
    """
    Populate claims dict.
    """
    claims['name'] = user.name
    claims['email'] = user.email

    # Get rest of information from Profile as a Service
    query = {'query': 'query{profiles(gcID: ' + str(user.id) + '){name, email, avatar, mobilePhone, officePhone,' +
                      'address{streetAddress,city, province, postalCode, country}}}'}

    response = requests.get(settings.GRAPHQL_ENDPOINT, headers={'Authorization':'Token ' + settings.GRAPHQL_TOKEN},
                            data=query)
    if not response.status_code == requests.codes.ok:
        raise Exception('Error getting user data / Server Response ' + str(response.status_code))
    else:
        response = response.json()
    if 'avatar' in response:
        claims['picture'] = response.get('avatar')
    if 'mobilePhone' in response or 'officePhone' in response:
        if 'mobilePhone' in response:
            claims['phone_number'] = response.get('mobilePhone')
        else:
            claims['phone_number'] = response.get('officePhone')
    if 'address' in response:
        claims['street_address'] = checkvalue(response['address']['streetAddress'])
        claims['locality'] = checkvalue(response['address']['city'])
        claims['region'] = checkvalue(response['address']['province'])
        claims['postal_code'] = checkvalue(response['address']['postalCode'])
        claims['country'] = checkvalue(response['address']['country'])

    return claims


def checkvalue(stringvalue):
    if stringvalue is not None:
        return stringvalue
    else:
        return ''

class CustomScopeClaims(ScopeClaims):

    info_modify_profile = (
        _('Profile Modification'),
        _('Ability to view and modify your profile information'),
    )

    def scope_modify_profile(self):
        # self.user - Django user instance.
        # self.userinfo - Dict returned by OIDC_USERINFO function.
        # self.scopes - List of scopes requested.
        # self.client - Client requesting this claims.
        dic = {
            'modify_profile': 'True',
            'read_profile': 'True'
        }

        return dic

    info_profile = (
        _('Basic profile'),
        _('Access to your name'),
    )

    info_detailed_profile = (
        _('Detailed User profile'),
        _('Access to your name, email, avatar, address, and organization information'),
    )

    def scope_read_profile(self):
        dic = {
            'read_profile': 'True',
        }

        return dic

