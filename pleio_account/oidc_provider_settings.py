"""
OIDC provider settings
"""
from oidc_provider.lib.claims import ScopeClaims
from django.utils.translation import ugettext as _

from urllib.parse import urlparse, urlencode
import urllib.request
import re


def userinfo(claims, user):
    """
    Populate default claims dict.
    """
    claims['name'] = user.name
    claims['email'] = user.email

    return claims


class CustomScopeCl(ScopeClaims):
    info_gcconnex = (
          _(u'GCconnex'),
          _(u'Profile data from GCconnex'),
    )

    def scope_gcconnex(self):
        # self.user - Django user instance.
        # self.userinfo - Dict returned by OIDC_USERINFO function.
        # self.scopes - List of scopes requested.
        # self.client - Client requesting this claims.

        # HACK: Temporary to get gconnex guid
        username = 'N/A'
        guid = '-1'

        search_url = "http://intranet.canada.ca/search-recherche/" \
                     "query-recherche-eng.aspx?a=s&s=3&chk4=on&%s" \
                     % urlencode({'q': self.user.email})
        with urllib.request.urlopen(search_url) as response:
            search_html = response.read()
            username_match = re.search(
                'href="https://gcconnex.gc.ca/profile/(.*?)"',
                search_html.decode('utf-8')
            )
            if username_match:
                username = username_match.group(1)
                profile_url = "https://gcconnex.gc.ca/profile/%s" % username
                with urllib.request.urlopen(profile_url) as profile_response:
                    profile_html = profile_response.read()
                    guid_match = re.search(
                        '"guid":(.*?),',
                        profile_html.decode('utf-8')
                    )
                    if guid_match:
                        guid = guid_match.group(1)

        claims = {
            'gcconnex_guid': guid,
            'gcconnex_username': username
        }

        return claims
