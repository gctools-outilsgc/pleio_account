from django.urls import reverse_lazy
from .forms import PleioAuthenticationTokenForm, PleioAuthenticationForm
from .models import User, PleioPartnerSite
from two_factor.forms import TOTPDeviceForm, BackupTokenForm
from two_factor.views.core import LoginView, SetupView, BackupTokensView
from two_factor.views.profile import ProfileView
from user_sessions.views import SessionListView, SessionDeleteOtherView, SessionDeleteView, LoginRequiredMixin
from django_otp.plugins.otp_static.models import StaticToken
from django.template.response import TemplateResponse
from django_otp import devices_for_user
from django.shortcuts import redirect
from django.views.generic.list import ListView
from django.utils.timezone import now
from django.contrib.auth.forms import AuthenticationForm

class PleioLoginView(LoginView):
    template_name = 'login.html'

    form_list = (
        #('auth', PleioAuthenticationForm),
        ('auth', AuthenticationForm),
        ('token', PleioAuthenticationTokenForm),
        ('backup', BackupTokenForm),
    )

    def get_context_data(self, **kwargs):
        context = super(PleioLoginView, self).get_context_data(**kwargs)
        next = self.request.GET.get('next')
        if next:
            context['next'] = next

        self.set_partner_site_info()

        return context

    def set_partner_site_info(self):
        try:
            http_referer = urlparse(self.request.META['HTTP_REFERER'])
        except:
            #no referer: cookies have to be deleted in PartnerSiteMiddleware
            self.request.COOKIES['partner_site_url'] = None
            self.request.COOKIES['partner_site_name'] = None
            self.request.COOKIES['partner_site_logo_url'] = None
            return False

        try:
            clean_url = http_referer.scheme+"://"+http_referer.netloc+"/"
            if http_referer.netloc == self.request.META['HTTP_HOST']:
                #referer is this site: no action to be taken
                return False

            try:
                #search for matching partnersite data
                partnersite = PleioPartnerSite.objects.get(partner_site_url=clean_url)
                self.request.COOKIES['partner_site_url'] = partnersite.partner_site_url
                self.request.COOKIES['partner_site_name'] = partnersite.partner_site_name
                self.request.COOKIES['partner_site_logo_url'] = partnersite.partner_site_logo_url
            except:
                try:
                    #no matching partnersite data found: default background image will be used
                    partnersite = PleioPartnerSite.objects.get(partner_site_url='http://localhost')
                    self.request.COOKIES['partner_site_url'] = clean_url
                    self.request.COOKIES['partner_site_name'] = http_referer.netloc
                    self.request.COOKIES['partner_site_logo_url'] = partnersite.partner_site_logo_url
                except:
                    return False
        except:
            return False

        return True

    def done(self, form_list, **kwargs):
        self.request.session.set_expiry(30 * 24 * 60 * 60)

        user = self.get_user()
        user.check_users_previous_logins(self.request)

        return LoginView.done(self, form_list, **kwargs)


class PleioProfileView(ProfileView):
    """
    View used by users for managing two-factor configuration.

    This view shows whether two-factor has been configured for the user's
    account. If two-factor is enabled, it also lists the primary verification
    method and backup verification methods.
    """
    def dispatch(self, request, *args, **kwargs):
        handler = getattr(self, 'get', self.http_method_not_allowed)

        self.request = request
        self.args = args
        self.kwargs = kwargs

        return handler(request, *args, **kwargs)


class PleioSessionListView(SessionListView):
    """
    View for listing a user's own sessions.

    This view shows list of a user's currently active sessions. You can
    override the template by providing your own template at
    `user_sessions/session_list.html`.
    """
    def dispatch(self, request, *args, **kwargs):
        handler = getattr(self, 'get', self.http_method_not_allowed)

        self.request = request
        self.args = args
        self.kwargs = kwargs

        return handler(request, *args, **kwargs)


class PleioSessionDeleteView(SessionDeleteView):
    """
    View for deleting all user's sessions but the current.

    This view allows a user to delete all other active session. For example
    log out all sessions from a computer at the local library or a friend's
    place.
    """
    def get_success_url(self):
        return str(reverse_lazy('security_pages'))


class PleioSessionDeleteOtherView(SessionDeleteOtherView):
    """
    View for deleting all user's sessions but the current.

    This view allows a user to delete all other active session. For example
    log out all sessions from a computer at the local library or a friend's
    place.
    """
    def get_success_url(self):
        return str(reverse_lazy('security_pages'))

class PleioBackupTokensView(BackupTokensView):
    """
    View for listing and generating backup tokens.

    A user can generate a number of static backup tokens. When the user loses
    its phone, these backup tokens can be used for verification. These backup
    tokens should be stored in a safe location; either in a safe or underneath
    a pillow ;-).
    """

    def get_context_data(self, **kwargs):
        context = super(BackupTokensView, self).get_context_data(**kwargs)
        device = self.get_device()
        context['device'] = device
        context['tokens'] = device.token_set.all()

        return context

    def form_valid(self, form):
        """
        Delete existing backup codes and generate new ones.
        """
        device = self.get_device()
        device.token_set.all().delete()
        for n in range(self.number_of_tokens):
            device.token_set.create(token=StaticToken.random_token())

        return TemplateResponse(self.request, 'security_pages.html', {
                'form': form,
                'tokens': device.token_set.all()
            })
