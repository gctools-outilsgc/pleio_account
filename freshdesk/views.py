import hashlib
import hmac
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.utils.http import urlquote
from django.views.decorators.cache import never_cache
from .models import Configuration


@never_cache
@login_required
def sso(request):
    if not request.user:
        raise Http404()

    name = request.user.name
    email = request.user.email
    dt = int(datetime.utcnow().strftime("%s")) - 148

    freshdesk_url = Configuration.objects.get(default=True).url
    freshdesk_secret_key = Configuration.objects.get(default=True).secret_key


    data = '{0}{1}{2}{3}'.format(name, freshdesk_url, email, dt)
    generated_hash = hmac.new(freshdesk_secret_key.encode(), data.encode(), hashlib.md5).hexdigest()
    url = freshdesk_url + 'login/sso/?name=' + urlquote(name) + '&email=' + urlquote(
        email) + '&' + u'timestamp=' + str(dt) + '&hash=' + generated_hash

    return HttpResponseRedirect(url)
