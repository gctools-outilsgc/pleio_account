from corsheaders.signals import check_request_enabled

# Required until fix implemented in django-oidc-provider
# to allow for OPTION on preflight request to userinfo
def cors_allow_api_to_everyone(sender, request, **kwargs):
    return request.path.startswith('/openid/userinfo')

check_request_enabled.connect(cors_allow_api_to_everyone)