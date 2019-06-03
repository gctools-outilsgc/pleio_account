from corsheaders.signals import check_request_enabled

from oidc_provider.models import Client

def cors_allow_mysites(sender, request, **kwargs):
    
    print("Remote Host key: %s" % (request.META["REMOTE_HOST"]))
    print("Remote Address key: %s" % (request.META["REMOTE_ADDR"]))
    
    ## Check to see if caller is localhost
    try :
        if request.META["REMOTE_ADDR"] == "127.0.0.1":
            return True
    except KeyError:
        return False
    redirects = Client.objects.filter(_redirect_uris___contains=request.META["REMOTE_HOST"]).exists
    return redirects

check_request_enabled.connect(cors_allow_mysites)