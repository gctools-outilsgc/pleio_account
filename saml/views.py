from django.shortcuts import render, redirect
from django.conf import settings
from django.core import signing
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib import messages
from django.db import IntegrityError
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseServerError, HttpRequest)
from django.utils.http import is_safe_url
from django.template import RequestContext
from django.utils.translation import gettext, gettext_lazy as _
from saml.models import IdentityProvider, ExternalId
from saml.forms import SetPasswordForm, ShowConnectionsForm
from core.models import User, EventLog
from core.class_views import PleioLoginView
from core.forms import PleioAuthenticationForm
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as auth_login
import requests
import os
import json
from core.forms import UserProfileForm
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

def init_saml_auth(req, idp_shortname=None):
    try:
        idp = IdentityProvider.objects.get(shortname=idp_shortname)
    except IdentityProvider.DoesNotExist:
        logger.error("saml.views.init_saml_auth,  no IdentityProvider found")
        idp = None
    
    if idp:
        configuration = {
            "strict": True,
            "debug": settings.DEBUG,
            "sp": settings.SAML2_SP,
            "idp": idp.get_saml_configuration()
        }

        auth = OneLogin_Saml2_Auth(req, configuration)
        return auth

    return None

def prepare_django_request(request, idp_shortname=None):
    '''
    If server is behind proxys or balancers use the HTTP_X_FORWARDED fields
    Check USE_X_FORWARDED_HOST and USE_X_FORWARDED_PORT in config.py
    ''' 
    req = {
        'https': 'on' if request.is_secure() else 'off',
        'http_host': request.get_host(),
        'script_name': request.META['PATH_INFO'],
        'server_port': request.get_port(),
        'get_data': request.GET.copy(),
        'post_data': request.POST.copy()
    }
    if idp_shortname:    
        request.session['idp'] = idp_shortname
    elif 'idp' in req['get_data']:
        request.session['idp'] = req['get_data']['idp']
    
    return req


def sso(request, idp_shortname):
    req = prepare_django_request(request, idp_shortname=idp_shortname)
    auth = init_saml_auth(req, idp_shortname=idp_shortname)

    return HttpResponseRedirect(auth.login())


@csrf_exempt
def acs(request):
    req = prepare_django_request(request)
    idp_shortname = request.session.get('idp') or None
    
    if not idp_shortname:
        return redirect(settings.LOGIN_REDIRECT_URL)        

    auth = init_saml_auth(req, idp_shortname=idp_shortname)

    auth.process_response()
    errors = auth.get_errors()
    next = request.session.get('next_saml', None)

    if not errors:
        attributes = auth.get_attributes()
        name_id = auth.get_nameid()
        session_index = auth.get_session_index()

        request.session['samlUserdata'] = attributes
        request.session['samlNameId'] = name_id
        request.session['samlSessionIndex'] = session_index
        ln = len(attributes.items())
        logger.error("saml.views.acs, number of attributes: " + str(ln))

        for attr in attributes.items():
            logger.error("saml.views.acs, attribute: " + str(attr))

        if type(attributes.get('emailaddress')) == list:
            email = attributes.get('emailaddress')[0]
        else:
            email = attributes.get('emailaddress')

        if not email:
            logger.error("saml.views.connect,  no emailaddress in samlUserdata found")
            messages.error(request, _("Email address not provided in saml request. Contact your system administrator." ), extra_tags="email_not_provided")
            if next:
                #connect SAML user with User
                #don't convert next string yet
                goto = settings.LOGIN_URL + '?next=' + next
            else:
                goto = settings.LOGIN_URL
            return redirect(goto)

        extid = check_externalid(request, shortname=idp_shortname, externalid=email)
        if not extid:
            if next:
                #connect SAML user with User
                #don't convert next string yet
                goto = settings.LOGIN_URL + '?next=' + next
            else:
                goto = settings.LOGIN_URL
            return redirect(goto)

        #now is time to convert next string to original value
        try:
            next = next.replace("%26", "&")
        except AttributeError:
            pass

        user = User.objects.get(pk=extid.userid.pk)

        pl = PleioLoginView()
        pl.post_login_process(request, user, next=next, extid=extid)
        if next and is_safe_url(next):
            return redirect(next)
    else:
        error_reason_code = auth.get_last_error_reason()
        logger.error("saml.views.acs, errors found: " + str(errors) + "reason: " + error_reason_code)

    if next and is_safe_url(next):
        goto = settings.LOGIN_REDIRECT_URL + '?next=' + next
    else:
        goto = settings.LOGIN_REDIRECT_URL

    return redirect(goto)

@csrf_exempt
def slo(request):
    req = prepare_django_request(request)
    if request.session.pop('slo', None):
        req['get_data']['slo'] = 'slo'

    idp_shortname = request.session.get('idp') or None
    
    if not idp_shortname:
        logger.error("saml.views.slo,  no IdentityProvider found")
        return redirect(settings.LOGIN_REDIRECT_URL)        

    auth = init_saml_auth(req, idp_shortname=idp_shortname)

    if 'slo' in req['get_data']:
        return HttpResponseRedirect(auth.logout(
            return_to=settings.LOGOUT_REDIRECT_URL,
            name_id=request.session.get('samlNameId'),
            session_index=request.session.get('samlSessionIndex')
        ))

    else:
         return redirect(settings.LOGOUT_REDIRECT_URL)

@csrf_exempt
def saml(request):
    # do nothing, because a user never logges in at our place
    return redirect(settings.LOGOUT_REDIRECT_URL)

def attrs(request):
    paint_logout = False
    attributes = False

    if 'samlUserdata' in request.session:
        paint_logout = True
        if len(request.session['samlUserdata']) > 0:
            attributes = request.session['samlUserdata'].items()

    return render(request, 'saml_attrs.html', 
                    context=RequestContext(request, {
                        'paint_logout': paint_logout, 
                        'attributes': attributes
                        }).flatten())


def metadata(request):
    ''' 
    req = prepare_django_request(request)
    auth = init_saml_auth(req)
    saml_settings = auth.get_settings()
    OneLogin is expecting the sp settings in settings.json in settings.SAML_FOLDER
    '''
    if not os.path.exists(settings.SAML_FOLDER):
        os.makedirs(settings.SAML_FOLDER)
    sp_metadata_file = open(settings.SAML_FOLDER+'/settings.json', 'w')
    sp_metadata = json.dumps({
        "strict": True,
        "debug": settings.DEBUG,
        "sp": settings.SAML2_SP,
    })
    sp_metadata_file.write(sp_metadata)
    sp_metadata_file.close()

    saml_settings = OneLogin_Saml2_Settings(settings=None, custom_base_path=settings.SAML_FOLDER, sp_validation_only=True)
    metadata = saml_settings.get_sp_metadata()
    errors = saml_settings.validate_metadata(metadata)

    if len(errors) == 0:
        resp = HttpResponse(content=metadata, content_type='text/xml')
    else:
        resp = HttpResponseServerError(content=', '.join(errors))
    return resp


def check_externalid(request, **kwargs):
    shortname=kwargs.get('shortname') 
    externalid=kwargs.get('externalid')
    try:
        idp = IdentityProvider.objects.get(shortname=shortname)
    except IdentityProvider.DoesNotExist:
        logger.warning("saml.views.check_externalid,  no IdentityProvider found")
        messages.error(request, _("IdentityProvider not found. Contact your system administrator." ), extra_tags="identityprovider_doesn't_exists")
        return None

    request.session['samlConnect'] = True

    try:
        extid = ExternalId.objects.get(identityproviderid=idp, externalid=externalid)
    except ExternalId.DoesNotExist:
        logger.warning("saml.views.check_externalid,  no ExternalId found")
        '''
        messages.info(request, _("Connect your organisation account with a " +
            settings.SITE_TITLE + 
            " " +
            "account"), 
            extra_tags="ExternalId_doesn't_exists")
        '''
        extid = None

    return extid


def connect_and_login(request):
    next = request.session.get('next_saml', None)
    #now is time to convert next string to original value
    try:
        next = next.replace("%26", "&")
    except AttributeError:
        pass

    extid = connect(request)
    if not extid:
        if next and is_safe_url(next):
            goto = settings.LOGIN_URL + '?next=' + next
        else:
            goto = settings.LOGIN_URL
        return redirect(goto)

    try:
        user = User.objects.get(pk=extid.userid.pk)
    except User.DoesNotExist:  
        logger.error("saml.views.connect_and_login,  can't connect, no existing user found")
        messages.error(request, _("Can't connect account for it doesn't seem to exists" ), extra_tags="user_doesn't_exists")
        return None

    pl = PleioLoginView()
    pl.post_login_process(request, user, next=next, extid=extid)

    if next and is_safe_url(next):
        return redirect(next)
    else:
        return redirect(settings.LOGIN_REDIRECT_URL) 


def connect(request, user_email=None):
    ''' 
    if user_email = None 
        a new  concierge account for this user has to be created
        saml account connects with this new concierge account 
    else saml account connects to existing concierge account    
    ''' 
    idp_shortname = request.session.get('idp') or None
    if not idp_shortname:
        return None        

    samlUserdata = request.session.get('samlUserdata') or None
    if samlUserdata:       
        if type(samlUserdata.get('emailaddress')) == list:
            email = samlUserdata.get('emailaddress')[0]
        else:
            email = samlUserdata.get('emailaddress')

    if not email:
        logger.error("saml.views.connect,  no emailaddress in samlUserdata found")
        messages.error(request, _("Email address not provided in saml request. Contact your system administrator." ), extra_tags="email_not_provided")
        return redirect(settings.LOGIN_REDIRECT_URL)        

    if samlUserdata:
        name = samlUserdata.get('name')
        if name and len(name) > 0:       
            if type(name) == list:
                name = name[0]
        
        if not name:
            givenname = samlUserdata.get('givenname')
            if givenname and len(givenname) > 0:       
                if type(givenname) == list:
                    givenname = givenname[0]
            if not givenname:
                givenname = ''
            surname = samlUserdata.get('surname')
            if surname and len(surname) > 0:       
                if type(surname) == list:
                    surname = surname[0]
            if not surname:
                surname = ''
            name = (givenname + ' ' + surname).strip()

        if not name or len(name) ==  0:
            name = email

    try:
        idp = IdentityProvider.objects.get(shortname=idp_shortname)
    except IdentityProvider.DoesNotExist:
        logger.error("saml.views.connect,  no IdentityProvider found")
        messages.error(request, _("IdentityProvider not found. Contact your system administrator." ), extra_tags="identityprovider_doesn't_exists")
        return None 

    if user_email:
        # connect to existing concierge account
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:  
            logger.error("saml.views.connect, can't connect, no existing user found")
            messages.error(request, _("Can't connect account for it doesn't seem to exists" ), extra_tags="user_doesn't_exists")
            return None
    else:
        try:
            user = User.objects.create_user(
                email=email,
                name=name,
                #password=signing.dumps(obj=email),
                accepted_terms=True,
                receives_newsletter=False
                )
            user.is_active=True
            user.save()
            user.send_set_password_activation_token()
        except IntegrityError:  
            logger.error("saml.views.connect, can't create, user already exists")
            messages.error(request, _("An account for this email address already exists" ), extra_tags='user_exists')
            return None

    try:
        extid = ExternalId.objects.get(identityproviderid=idp, externalid=email)
    except ExternalId.DoesNotExist:
        extid= ExternalId.objects.create(
            identityproviderid=idp,
            externalid=email,
            userid=user
        )

    return extid


def set_new_password(request, activation_token=None):
    if request.method == 'POST':
        user = request.user
        form = SetPasswordForm(request.POST, user=user)
        if form.is_valid():
            data = form.cleaned_data
            user.set_password(data['new_password2'])
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, _('Password changed'), extra_tags='password')
            return redirect('profile')
        else:
            return render(request, 'set_new_password.html', { 'form': form })
    else:
        user = User.set_new_password(None, activation_token)
        if not user:
            return redirect(settings.LOGIN_URL)
        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        form = SetPasswordForm()
        return render(request, 'set_new_password.html', { 'form': form })

    return redirect(settings.LOGIN_URL)


def show_connections(request):
    connections = ExternalId.objects.filter(userid=request.user)    

    return render(request, 'show_connections.html', {'connections': connections})


def delete_connection(request, pk=None):
    if pk:
        try:
            connection = ExternalId.objects.get(pk=pk).delete()
        except:
            pass

    return redirect('saml_connections')

