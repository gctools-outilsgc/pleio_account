import time
import hmac
import hashlib
import urllib.parse
from base64 import b32encode
from binascii import unhexlify

import django_otp
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django_otp.util import random_hex

from django.contrib.auth import update_session_auth_hash
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.views.decorators.cache import never_cache

from core.class_views import (
    PleioBackupTokensView,
    PleioSessionListView,
    PleioProfileView
)
from two_factor.views.profile import DisableView

from .forms import (
    RegisterForm,
    UserProfileForm,
    PleioTOTPDeviceForm,
    ChangePasswordForm
)
from .models import User, PreviousLogins, SiteConfiguration

DEFAULT_AVATAR = '/static/images/user.svg'


def home(request):
    if request.user.is_authenticated():
        return redirect('profile')
    return redirect('login')


def logout(request):
    auth.logout(request)
    return redirect('login')


def register(request):
    if request.user.is_authenticated():
        return redirect('profile')

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                user = User.objects.create_user(
                    name=data['name'],
                    email=data['email'],
                    password=data['password2'],
                    accepted_terms=data['accepted_terms'],
                    receives_newsletter=True
                )
            except Exception:
                user = User.objects.get(email=data['email'])

            if not user.is_active:
                user.send_activation_token(request)

            return redirect('register_complete')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def register_complete(request):
    return render(request, 'register_complete.html')


def register_activate(request, activation_token=None):
    if request.user.is_authenticated():
        return redirect('profile')

    user = User.activate_user(None, activation_token)

    if user:
        auth.login(
            request,
            user,
            backend='django.contrib.auth.backends.ModelBackend'
        )
        return redirect('profile')

    return render(request, 'register_activate.html')


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=request.user
        )
        if form.is_valid():
            form.save()
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'profile.html', {'form': form})


def avatar(request):
    try:
        user = User.objects.get(id=int(request.GET['guid']))
        if user.avatar:
            return redirect('/media/' + str(user.avatar))
    except User.DoesNotExist:
        pass

    return redirect(DEFAULT_AVATAR)


def accept_previous_login(request, acceptation_token=None):
    try:
        PreviousLogins.accept_previous_logins(request, acceptation_token)
    except Exception:
        pass
    return redirect('profile')


def terms_of_use(request):

    return render(request, 'terms_of_use.html')


@login_required
def security_pages(request, page_action=None):
    return render(request, 'security_pages.html', {
        'pass_reset_form': change_password_form(request, page_action),
        '2FA': two_factor_form(request, page_action),
        'user_session_form': user_sessions_form(request)
    })


def change_password_form(request, page_action):
    if page_action == 'change-password':
        user = request.user
        form = ChangePasswordForm(request.POST, user=user)
        if form.is_valid():
            data = form.cleaned_data
            user.set_password(data['new_password2'])
            user.save()
            update_session_auth_hash(request, user)
            messages.success(
                request,
                _('The Password has been changed successfully.')
            )
    else:
        form = ChangePasswordForm()

    return form


def two_factor_form(request, page_action):
    two_factor_authorization = {}
    if page_action == '2fa-setup':
        key = random_hex(20).decode('ascii')
        rawkey = unhexlify(key.encode('ascii'))
        b32key = b32encode(rawkey).decode('utf-8')

        request.session['tf_key'] = key
        request.session['django_two_factor-qr_secret_key'] = b32key

        two_factor_authorization = ({
            'form': PleioTOTPDeviceForm(key=key, user=request.user),
            'QR_URL': reverse('two_factor:qr')
        })
        two_factor_authorization['state'] = 'setup'
    elif page_action == '2fa-setupnext':
        key = request.session.get('tf_key')
        form = PleioTOTPDeviceForm(
            data=request.POST,
            key=key,
            user=request.user
        )
        if form.is_valid():
            device = form.save()
            django_otp.login(request, device)
            two_factor_authorization['default_device'] = True
            two_factor_authorization['show_state'] = True
        else:
            two_factor_authorization['form'] = form
            two_factor_authorization['QR_URL'] = reverse('two_factor:qr')
            two_factor_authorization['state'] = 'setup'
    elif page_action == '2fa-disable':
        two_factor_authorization = DisableView.as_view(
            template_name='security_pages.html'
        )(request).context_data
        two_factor_authorization['state'] = 'disable'
    elif page_action == '2fa-disableconfirm':
        two_factor_authorization = DisableView.as_view(
            template_name='security_pages.html'
        )(request)
        two_factor_authorization['state'] = 'default'
        two_factor_authorization['show_state'] = 'true'
    elif page_action == '2fa-showcodes':
        two_factor_authorization = PleioBackupTokensView.as_view(
            template_name='backup_tokens.html'
        )(request).context_data
        two_factor_authorization['default_device'] = 'true'
        two_factor_authorization['state'] = 'codes'
        two_factor_authorization['show_state'] = 'true'
    elif page_action == '2fa-generatecodes':
        two_factor_authorization = PleioBackupTokensView.as_view(
            template_name='security_pages.html'
        )(request).context_data
        two_factor_authorization['default_device'] = 'true'
        two_factor_authorization['show_state'] = 'true'
        two_factor_authorization['state'] = 'codes'
    else:
        two_factor_authorization = PleioProfileView.as_view(
            template_name='security_pages.html'
        )(request).context_data
        two_factor_authorization['state'] = 'default'
        two_factor_authorization['show_state'] = 'true'

    return two_factor_authorization


def user_sessions_form(request):
    user_sessions = PleioSessionListView.as_view(
        template_name='security_pages.html'
    )(request).context_data
    return user_sessions['object_list']


@never_cache
@login_required
def freshdesk_sso(request):
    if not request.user:
        raise Http404()

    name = request.user.name
    email = request.user.email
    dt = int(time.time()) - 148

    site_config = SiteConfiguration.objects.get()
    config_data = site_config.get_values()

    data = '{0}{1}{2}{3}'.format(name, config_data['freshdesk_key'], email, dt)
    generated_hash = hmac.new(
        config_data['freshdesk_key'].encode(),
        data.encode(),
        hashlib.md5
    ).hexdigest()

    return HttpResponseRedirect('{url}login/sso/?{args}'.format(
        url=config_data['freshdesk_url'],
        args=urllib.parse.urlencode({
            'name': name,
            'email': email,
            'timestamp': str(dt),
            'hash': generated_hash
        })
    ))

