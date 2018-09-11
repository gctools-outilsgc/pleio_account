import hashlib
import hmac
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.utils.http import urlquote
from django.views.decorators.cache import never_cache
from freshdesk import settings


@never_cache
@login_required
def sso(request):
    if not request.user:
        raise Http404()

    name = request.user.name
    email = request.user.email
    dt = int(datetime.utcnow().strftime("%s")) - 148

    data = '{0}{1}{2}{3}'.format(name, settings.FRESHDESK_SECRET_KEY, email, dt)
    generated_hash = hmac.new(settings.FRESHDESK_SECRET_KEY.encode(), data.encode(), hashlib.md5).hexdigest()
    url = settings.FRESHDESK_URL + 'login/sso/?name=' + urlquote(name) + '&email=' + urlquote(
        email) + '&' + u'timestamp=' + str(dt) + '&hash=' + generated_hash

    return HttpResponseRedirect(url)
