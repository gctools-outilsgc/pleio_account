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
from core.class_views import PleioBackupTokensView
from two_factor.views.profile import DisableView
from .helpers import str2dict


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

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                name=data['name'],
                email=data['email'],
                password=data['password2'],
                accepted_terms=data['accepted_terms'],
                receives_newsletter=data['receives_newsletter']
            )

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
        auth.login(request, user)
        return redirect('profile')

    return render(request, 'register_activate.html')


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()

    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'profile.html', {'form': form})


def avatar(request):
    DEFAULT_AVATAR = '/static/images/gebruiker.svg'

    #print(request.GET['guid'])
    user = User.objects.get(id=request.GET['guid'])
    #print(user.avatar)

    try:
        user = User.objects.get(id=int(request.GET['guid']))
        if user.avatar:
            return redirect('/media/' + str(user.avatar))
    except User.DoesNotExist:
        pass

    return redirect(DEFAULT_AVATAR)


@login_required
def tf_setup(request):
    key = random_hex(20).decode('ascii')
    rawkey = unhexlify(key.encode('ascii'))
    b32key = b32encode(rawkey).decode('utf-8')

    request.session['tf_key'] = key
    request.session['django_two_factor-qr_secret_key'] = b32key

    return TemplateResponse(request, 'security_pages.html', {
        'form': PleioTOTPDeviceForm(key=key, user=request.user),
        'QR_URL': reverse('two_factor:qr')
    })
    
@login_required
def tf_setup_complete(request):
    if request.method == 'POST':
        key = request.session.get('tf_key')
        form = PleioTOTPDeviceForm(data=request.POST, key=key, user=request.user)

        if form.is_valid():
            device = form.save()
            django_otp.login(request, device)
            return True

        try:
            print("token fout: ", form.errors.get('token'))
            errormessage = form.errors.get('token')
            messages.error(request, errormessage)
            return False
        except:
            pass

        return True


def accept_previous_login(request, acceptation_token=None):
    try:
        PreviousLogins.accept_previous_logins(request, acceptation_token)
    except:
        pass

    return redirect('profile')


def terms_of_use(request):

    return render(request, 'terms_of_use.html')


@login_required
def security_pages(request, *args, **kwargs):

    if request.method == 'POST':
        page_action = request.POST.get('page_action')

        if page_action == 'ChangePassword':
            form = ChangePasswordForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                old_password = data['old_password']
                new_password1 = data['new_password1']
                new_password2 = data['new_password2']
                username = request.user.email
                user = authenticate(username=username, password=old_password)
                if user:
                    user.set_password(data['new_password2'])
                    user.save()
                    update_session_auth_hash(request, user)
                    astring =  'The Password has been changed successfully.'
                    aheader = '<ul class="message_success"><li>'
                    atrailer = '</li></ul>'
                    amsg = aheader + astring + atrailer
                    messages.error(request, _(amsg) , extra_tags='safe')
                    #messages.success(request, _('The Password has been changed successfully.'))
                else:
                    astring =  'The current Password is invalid'
                    aheader = '<ul class="errorlist"><li>'
                    atrailer = '</li></ul>'
                    amsg = aheader + astring + atrailer
                    messages.error(request, _(amsg) , extra_tags='safe')
            else:
                try:
                    errormessage = form.errors.get('new_password1')
                    messages.error(request, errormessage)
                except:
                    pass
                try:
                    errormessage = form.errors.get('new_password2')
                    messages.error(request, errormessage)
                except:
                    pass
 
            return redirect('security_pages')

        if page_action == '2FASetUp':
            two_factor_authorization = tf_setup(request).context_data
            two_factor_authorization['default_device'] = 'true'
            two_factor_authorization['state'] = 'setup'

            response = redirect('security_pages', page_action='2FASetUp')
            response.set_cookie('2FA', two_factor_authorization)
            return response

        elif page_action == '2FASetUpNext':
            if tf_setup_complete(request):
                return redirect('security_pages')
            else:
                return redirect('security_pages', page_action='2FASetUp')


        elif page_action == '2FAGenerateCodes':
            two_factor_authorization = PleioBackupTokensView.as_view(template_name='security_pages.html')(request).context_data
            two_factor_authorization['default_device'] = 'true'
            two_factor_authorization['show_state'] = 'true'
            two_factor_authorization['state'] = 'codes'

            response = redirect('security_pages', page_action='2FAShowCodes')
            response.set_cookie('2FA', two_factor_authorization)
            return response

        elif page_action == '2FADisableConfirm':
            two_factor_authorization = DisableView.as_view(template_name='security_pages.html')(request)
            two_factor_authorization['state'] = 'disable'
            return redirect('security_pages')

    if request.method == 'GET':
        page_action = request.GET.get('page_action')
        if 'page_action' in kwargs:
            page_action = kwargs['page_action']
        print('get page_action: ', page_action)

        if page_action == '2FAShowCodes':
            two_factor_authorization = PleioBackupTokensView.as_view(template_name='backup_tokens.html')(request).context_data
            two_factor_authorization['default_device'] = 'true'
            two_factor_authorization['state'] = 'codes'
            two_factor_authorization['show_state'] = 'true'
        elif page_action == '2FADisable':
            two_factor_authorization = DisableView.as_view(template_name='security_pages.html')(request).context_data
            two_factor_authorization['state'] = 'disable'
        elif page_action == '2FASetUp':
            #two_factor_authorization = tf_setup(request).context_data
            two_factor_authorization = str2dict(request.COOKIES['2FA'])
        else:
            two_factor_authorization = ProfileView.as_view(template_name='security_pages.html')(request).context_data
            two_factor_authorization['state'] = 'default'
            two_factor_authorization['show_state'] = 'true'

        user_sessions = SessionListView.as_view(template_name='security_pages.html')(request).context_data

        return render(request, 'security_pages.html',
                {
                    'pass_reset_form': ChangePasswordForm(),
                    '2FA': two_factor_authorization,
                    'object_list': user_sessions['object_list']
                })

    return redirect('security_pages')

