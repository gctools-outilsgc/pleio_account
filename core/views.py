from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, UserProfileForm, PleioTOTPDeviceForm, ChangePasswordForm
from .models import User, PreviousLogins
from django.urls import reverse
from base64 import b32encode
from binascii import unhexlify
from django_otp.util import random_hex
import django_otp
from django.conf import settings

from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, update_session_auth_hash
from two_factor.views import ProfileView
from user_sessions.views import SessionListView
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib import messages
from django.template.response import TemplateResponse
from django.contrib.auth import password_validation
from core.class_views import PleioBackupTokensView, PleioSessionListView, PleioProfileView
from two_factor.views.profile import DisableView


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
                    receives_newsletter=data['receives_newsletter']
                )
            except:
                user = User.objects.get(email=data['email'])

            user.send_activation_token()

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
        auth.login(request, user)
        return redirect('profile')

    return render(request, 'register_activate.html')


def change_email(request):
    #user = User.objects.get(email=data['email'])
    user = request.user
    user.send_change_email_activation_token()

    return redirect('profile')

def change_email_activate(request, activation_token=None):
    user = User.change_email(None, activation_token)

    if user:
        messages.success(request, _('Email address changed'), extra_tags='email')

    return redirect('profile')

@login_required
def profile(request):
    if request.method == 'POST':
        new_email_save = request.user.new_email
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            data = form.cleaned_data
            new_email = data['new_email']
            user = form.save()
            user.new_email = new_email
            user.save()
            if new_email and (new_email != new_email_save):
                change_email(request)
            form = UserProfileForm(instance=request.user)
    else:
        form = UserProfileForm(instance=request.user)

    if request.user.new_email:
        text_change_pending = _('There is a pending change of your email to ')
    else:
        text_change_pending = None

    return render(request, 'profile.html', {'form': form, 'text_change_pending': text_change_pending, 'text_email': request.user.new_email})


def avatar(request):
    DEFAULT_AVATAR = '/static/images/gebruiker.svg'

    user = User.objects.get(id=request.GET['guid'])

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
    except:
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
            new_password2 = data['new_password2']
            user.set_password(data['new_password2'])
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, _('Password changed'), extra_tags='password')
    else:
        form = ChangePasswordForm()

    return form

def two_factor_form(request, page_action):
    two_factor_authorization =  {}
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
        form = PleioTOTPDeviceForm(data=request.POST, key=key, user=request.user)
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
        two_factor_authorization = DisableView.as_view(template_name='security_pages.html')(request).context_data
        two_factor_authorization['state'] = 'disable'

    elif page_action == '2fa-disableconfirm':
        two_factor_authorization = DisableView.as_view(template_name='security_pages.html')(request)
        two_factor_authorization['state'] = 'default'
        two_factor_authorization['show_state'] = 'true'

    elif page_action == '2fa-showcodes':
        two_factor_authorization = PleioBackupTokensView.as_view(template_name='backup_tokens.html')(request).context_data
        two_factor_authorization['default_device'] = 'true'
        two_factor_authorization['state'] = 'codes'
        two_factor_authorization['show_state'] = 'true'

    elif page_action == '2fa-generatecodes':
        two_factor_authorization = PleioBackupTokensView.as_view(template_name='security_pages.html')(request).context_data
        two_factor_authorization['default_device'] = 'true'
        two_factor_authorization['show_state'] = 'true'
        two_factor_authorization['state'] = 'codes'

    else:
        two_factor_authorization = PleioProfileView.as_view(template_name='security_pages.html')(request).context_data
        two_factor_authorization['state'] = 'default'
        two_factor_authorization['show_state'] = 'true'

    return two_factor_authorization

def user_sessions_form(request):
    user_sessions = PleioSessionListView.as_view(template_name='security_pages.html')(request).context_data

    return user_sessions['object_list']
