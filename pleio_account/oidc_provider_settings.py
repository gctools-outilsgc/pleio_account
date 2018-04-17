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
    query = {'query': 'query{profiles(gcID: "' + str(user.id) + '"){name, email, avatar, mobilePhone, officePhone,' +
                      'address{streetAddress,city, province, postalCode, country}}}'}

    response = requests.post(settings.GRAPHQL_ENDPOINT, headers={'Authorization': 'Token ' + settings.GRAPHQL_TOKEN},
                             data=query)
    if not response.status_code == requests.codes.ok:
        raise Exception('Error getting user data / Server Response ' + str(response.status_code))
    else:
        response = response.json()
        response_address = response['data']['profiles'][0].get('address')

        claims['picture'] = checkvalue(response['data']['profiles'][0].get('avatar'))
        if response['data']['profiles'][0].get('mobilePhone') is not None:
            claims['phone_number'] = checkvalue(response['data']['profiles'][0].get('mobilePhone'))
        else:
            claims['phone_number'] = checkvalue(response['data']['profiles'][0].get('officePhone'))

        if response_address is not None:

            if 'streetAddress' in response_address:
                claims['address']['street_address'] = checkvalue(response_address.get('streetAddress'))
            if 'city' in response_address:
                claims['address']['locality'] = checkvalue(response_address.get('city'))
            if 'province' in response_address:
                claims['address']['region'] = checkvalue(response_address.get('province'))
            if 'postalCode' in response_address:
                claims['address']['postal_code'] = checkvalue(response_address.get('postalCode'))
            if 'country' in response_address:
                claims['address']['country'] = checkvalue(response_address.get('country'))

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
            'detailed_profile': 'True'
        }

        return dic

    info_profile = (
        _('Basic profile'),
        _('Access to your name, email, avatar, and address'),
    )

    info_detailed_profile = (
        _('Detailed User profile'),
        _('Access to your name, email, avatar, address, and organization information'),
    )

    def scope_detailed_profile(self):
        dic = {
            'detailed_profile': 'True',
        }

        return dic

