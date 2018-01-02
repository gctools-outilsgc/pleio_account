"""
OIDC provider settings
"""


def userinfo(claims, user):
    """
    Populate claims dict.
    """
    claims['name'] = user.name
    claims['email'] = user.email

    return claims
