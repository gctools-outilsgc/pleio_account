from django.urls import reverse_lazy
from .forms import PleioAuthenticationTokenForm, PleioAuthenticationForm, PleioBackupTokenForm
from .models import User, PleioPartnerSite, EventLog
from two_factor.forms import TOTPDeviceForm, BackupTokenForm
from two_factor.views.core import LoginView, SetupView, BackupTokensView
from two_factor.views.profile import ProfileView
from user_sessions.views import SessionListView, SessionDeleteOtherView, SessionDeleteView, LoginRequiredMixin
from django_otp.plugins.otp_static.models import StaticToken
from django.template.response import TemplateResponse
from django_otp import devices_for_user
from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.utils.timezone import now
from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.generic import TemplateView
from django.contrib.auth import login as auth_login
from two_factor.utils import default_device
import django_otp
from urllib.parse import urlparse

class PleioLoginView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super(PleioLoginView, self).get_context_data(**kwargs)
        next = self.request.GET.get('next')
        if next:
            context['next'] = next
            self.request.session['next'] = next
        
        self.set_partner_site_info()

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        next = request.session.get('next')
        if not is_safe_url(next):
            next = ''
        login_step = kwargs.get('login_step')
        if login_step:
            request.session['login_step'] = login_step
        else:
            login_step = request.session.get('login_step')

        if not login_step:
            login_step = 'login'
            request.session['login_step'] = login_step

        if login_step == 'login':
            form = PleioAuthenticationForm(request=request)
        elif login_step == 'token':
            user = User.objects.get(email=request.session.get('username'))
            form = PleioAuthenticationTokenForm(user, request)
        elif login_step == 'backup':
            user = User.objects.get(email=request.session.get('username'))
            form = PleioBackupTokenForm(user, request)

        return render(request, 'login.html', { 
                    'form' : form, 
                    'login_step' : login_step,
                    'reCAPTCHA' : EventLog.reCAPTCHA_needed(request),
                    'next' : next 
                    })

    def post(self, request, *args, **kwargs):
        login_step = kwargs.get('login_step')
        if login_step:
            request.session['login_step'] = login_step
        else:
            login_step = request.session.get('login_step')

        if login_step == 'login':
            response = self.post_login(request, *args, **kwargs)
        elif login_step == 'token':
            response = self.post_token(request, *args, **kwargs)
        elif login_step == 'backup':
            response = self.post_backuptoken(request, *args, **kwargs)

        return response
            
    def post_login(self, request, *args, **kwargs):
        next = request.POST.get('next')
        if not is_safe_url(next):
            next = settings.LOGIN_REDIRECT_URL
        form = PleioAuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            user = User.objects.get(email=username)
            request.session['username'] = username
            device = default_device(user)
            if not device:
                auth_login(request, user)
                return redirect(next)
            else:
                request.session['login_step'] = 'token'
                form = PleioAuthenticationTokenForm(user, request)
        else:
            for key, value in form.errors.items():
                if value[0] == 'inactive':
                    try:
                        username = request.POST.get('username')
                        user = User.objects.get(email=username)
                        user.send_activation_token()
                        return redirect('register_complete')
                    except:
                        pass
            EventLog.add_event(request, 'invalid login')

        return render(request, 'login.html', {
            'form' : form, 
            'login_step' : request.session.get('login_step'),
            'reCAPTCHA' : EventLog.reCAPTCHA_needed(request), 
            'next' : next 
            }
        )

    def post_token(self, request, *args, **kwargs):
        next = request.POST.get('next')
        if not is_safe_url(next):
            next = settings.LOGIN_REDIRECT_URL
        user = User.objects.get(email=request.session.get('username'))
        form = PleioAuthenticationTokenForm(user, request, data=request.POST)
        if form.is_valid():
            auth_login(request, user)
            return redirect(next)
        else:
            EventLog.add_event(request, 'invalid login')

        return render(request, 'login.html', {'form' : form, 'login_step' : request.session.get('login_step') })

    def post_backuptoken(self, request, *args, **kwargs):
        next = request.POST.get('next')
        if not is_safe_url(next):
            next = settings.LOGIN_REDIRECT_URL
        user = User.objects.get(email=request.session.get('username'))
        form = PleioBackupTokenForm(user, request, data=request.POST)
        if form.is_valid():
            auth_login(request, user)
            return redirect(next)
        else:
            EventLog.add_event(request, 'invalid login')

        return render(request, 'login.html', {'form' : form, 'login_step' : request.session.get('login_step') })
    
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
