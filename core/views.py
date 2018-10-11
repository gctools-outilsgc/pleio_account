from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, UserProfileForm, PleioTOTPDeviceForm, ChangePasswordForm, ChooseSecurityQuestion, AnswerSecurityQuestions
from .models import User, PreviousLogins, SecurityQuestions
from django.urls import reverse
from base64 import b32encode
from binascii import unhexlify
from django_otp.util import random_hex
import django_otp
from django.conf import settings

from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import make_password
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from two_factor.views import ProfileView
from user_sessions.views import SessionListView
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib import messages
from django.template.response import TemplateResponse
from django.contrib.auth import password_validation
from core.class_views import PleioBackupTokensView, PleioSessionListView, PleioProfileView
from two_factor.views.profile import DisableView

from django.http import Http404, HttpResponseRedirect
from django.views.decorators.cache import never_cache
from django.utils.http import urlquote
from datetime import datetime
import hashlib
import hmac
import random

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
            except:
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
        auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
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
    DEFAULT_AVATAR = '/static/images/user.svg'

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


def security_questions(request):

    #bring user back to start
    if 'email' not in request.session:
        return redirect('password_reset')

    user = User.objects.get(email=request.session['email'])
    try:
        questions = SecurityQuestions.objects.get(user=user)
    except SecurityQuestions.DoesNotExist:
        questions = None
    has_questions = False if questions is None else True

    if has_questions:
        picks = [1,2,3]
        random.shuffle(picks)
        if 'picks' not in request.session:
            request.session['picks'] = picks
        picked_questions = questions.get_questions(request.session['picks'][0],request.session['picks'][1])
    else:
        picked_questions = {}

    form = AnswerSecurityQuestions()
    if request.method == "POST":
        form = AnswerSecurityQuestions(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            del request.session['email']
            del request.session['picks']
            return redirect(request.is_secure() and "https" or "http" + '://' +
            request.META['HTTP_HOST'] +
            '/reset/' +
             (urlsafe_base64_encode(force_bytes(user.pk))).decode('utf-8') + '/' +
             default_token_generator.make_token(user)
             )

    return render(request, 'password_reset_questions.html', {
        'form': form,
        "has_questions": has_questions,
        "questions": picked_questions,
        "picks": request.session['picks']
    })

@login_required
def security_pages(request, page_action=None):

    return render(request, 'security_pages.html', {
        'pass_reset_form': change_password_form(request, page_action),
        'security_questions': security_question(request),
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
            messages.success(request, _('The Password has been changed successfully.'))
    else:
        form = ChangePasswordForm()

    return form

def security_question(request):
    security_questions = {}
    return security_questions

def set_security_question(request):

    form = ChooseSecurityQuestion()
    if request.method == 'POST':
        form = ChooseSecurityQuestion(request.POST)
        if form.is_valid():
            #check to see if user already set questions
            try:
                questions = SecurityQuestions.objects.get(user=request.user)
            except SecurityQuestions.DoesNotExist:
                questions = None

            data = form.cleaned_data
            if questions == None:
                new_question = SecurityQuestions.objects.create(
                    user=request.user,
                    question_1=data['question_one'],
                    answer_1=make_password(data['answer_one'].lower()),
                    question_2=data['question_two'],
                    answer_2=make_password(data['answer_two'].lower()),
                    question_3=data['question_three'],
                    answer_3=make_password(data['answer_three'].lower())
                )
                new_question.save()
            else:
                questions.question_1=data['question_one']
                questions.answer_1=make_password(data['answer_one'].lower())
                questions.question_2=data['question_two']
                questions.answer_2=make_password(data['answer_two'].lower())
                questions.question_3=data['question_three']
                questions.answer_3=make_password(data['answer_three'].lower())
                questions.save()

            messages.success(request, _('Your security questions and answers have been successfully saved.'))
            return redirect('security_pages')

    return render(request, 'security_pages_questions.html', { 'form': form })

    return security_questions

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

@never_cache
@login_required
def freshdesk_sso(request):
    if not request.user:
        raise Http404()

    name = request.user.name
    email = request.user.email
    dt = int(datetime.utcnow().strftime("%s")) - 148

    data = '{0}{1}{2}{3}'.format(name, settings.FRESHDESK_SECRET_KEY, email, dt)
    generated_hash = hmac.new(settings.FRESHDESK_SECRET_KEY.encode(), data.encode(), hashlib.md5).hexdigest()
    url = settings.FRESHDESK_URL+'login/sso/?name='+urlquote(name)+'&email='+urlquote(email)+'&'+u'timestamp='+str(dt)+'&hash='+generated_hash

    return HttpResponseRedirect(url)
