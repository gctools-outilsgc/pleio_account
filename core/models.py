from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import get_language, gettext, gettext_lazy as _
from django.utils.safestring import mark_safe
from django.core import signing
from django.core.mail import send_mail
from django.contrib import admin
from django.contrib.sites.shortcuts import get_current_site
from django.db import models
from django.conf import settings
from django.template.loader import render_to_string
from .tasks import send_mail
from .helpers import unique_avatar_filepath, unique_avatar_large_filename, unique_avatar_medium_filename
from .helpers import unique_avatar_small_filename, unique_avatar_tiny_filename, unique_avatar_topbar_filename
from .login_session_helpers import get_city, get_country, get_device, get_lat_lon
from datetime import timedelta
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

class Manager(BaseUserManager):
    def create_user(self, email, name, password=None, accepted_terms=False, receives_newsletter=False):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name
        )

        user.set_password(password)
        user.accepted_terms = accepted_terms
        user.receives_newsletter = receives_newsletter

        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(
            email=self.normalize_email(email),
            name=name,
            password=password
        )

        user.is_admin = True
        user.is_active = True
        user.receives_newsletter = True

        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    objects = Manager()

    username = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True)
    accepted_terms = models.BooleanField(default=False)
    receives_newsletter = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to=unique_avatar_filepath, null=True, blank=True)
    new_email = models.CharField(max_length=255, null=True, blank=True, default=None)
    time_created = models.DateTimeField(default=timezone.now)

    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)

    __saved_avatar = None

    REQUIRED_FIELDS = ['name']
    USERNAME_FIELD = 'email'

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        if self.avatar:
            self.__saved_avatar = self.avatar

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self._get_unique_username()
        if self.avatar != self.__saved_avatar:
            ResizedAvatars.make_avatars(self, self.avatar)

        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.email

    def _get_unique_username(self):
        max_length = User._meta.get_field('username').max_length
        username = slugify(self.email.split("@")[0])
        unique_username = username[:max_length]
        i = 1

        while User.objects.filter(username=unique_username).exists():
            unique_username = '{}{}'.format(username[:max_length - len(str(i)) - 1], i)
            i += 1

        return unique_username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def email_user(self, subject, message, **kwargs):
        email = kwargs.pop('email', self.email)

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], **kwargs)

    def send_activation_token(self):
        template_context = {
            'user': self,
            'activation_token': signing.dumps(obj=self.email),
        }

        self.email_user(
            render_to_string('emails/register_subject.txt', template_context),
            render_to_string('emails/register.txt', template_context),
            html_message = (render_to_string('emails/register.html', template_context)),
            fail_silently = True
        )

    def send_set_password_activation_token(self):
        template_context = {
            'user': self,
            'activation_token': signing.dumps(obj=self.email),
        }

        self.email_user(
            render_to_string('emails/set_new_password_subject.txt', template_context),
            render_to_string('emails/set_new_password.txt', template_context),
            html_message = (render_to_string('emails/set_new_password.html', template_context)),
            fail_silently = True,
            email=self.email
        )

    def send_change_email_activation_token(self):
        template_context = {
            'user': self,
            'activation_token': signing.dumps(obj=self.new_email),
        }
 
        self.email_user(
            render_to_string('emails/change_email_subject.txt', template_context),
            render_to_string('emails/change_email.txt', template_context),
            html_message = (render_to_string('emails/change_email.html', template_context)),
            fail_silently = True,
            email=self.new_email
        )

    def activate_user(self, activation_token):
        try:
            email = signing.loads(
                activation_token,
                max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400
            )

            if email is None:
                return None

            self = User.objects.get(email=email)

            if self.is_active:
                return None

            self.is_active = True
            self.save()

            return self

        except (signing.BadSignature, User.DoesNotExist):
            return None

    def change_email(self, activation_token):
        try:
            email = signing.loads(
                activation_token,
                max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400
            )

            if email is None:
                return None

            self = User.objects.get(new_email=email)

            self.email = self.new_email
            self.new_email = None
            self.save()

            return self

        except (signing.BadSignature, User.DoesNotExist):
            return None

    def set_new_password(self, activation_token):
        try:
            email = signing.loads(
                activation_token,
                max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400
            )

            self = User.objects.get(email=email)

            return self

        except (signing.BadSignature, User.DoesNotExist):
            return None

    def check_users_previous_logins(self, request):
        send_suspicious_behavior_warnings = settings.SEND_SUSPICIOUS_BEHAVIOR_WARNINGS

        result = True

        try:
            device_id = request.COOKIES['device_id']
            login = self.previous_logins.get(device_id=device_id)
            previous_login_present = login.confirmed_login
        except:
            previous_login_present = False

        if previous_login_present:
            # cookie is present so no need to send an email and no further checking is requiered
            send_suspicious_behavior_warnings = False
            login.update_previous_login(request)

        if send_suspicious_behavior_warnings:
            if not self.logged_in_previously(request):
                # no confirmed matching login found, so email must be sent
                self.send_suspicious_login_message(request)
                result = False

        return result

    def logged_in_previously(self, request):
        # check whether user has previously logged in from this location and using this device
        session = request.session

        login = self.previous_logins.filter(
            ip=session.ip,
            user_agent=get_device(session.user_agent)
        )

        known_login = (login.count() > 0)

        if not known_login:
            # request.user is atm still "Anonymoususer", so have to add self as second arg
            PreviousLogins.add_known_login(request, self)
        else:
            login[0].update_previous_login(request)

        login = login.filter(confirmed_login=True)
        confirmed_login = (login.count() > 0)

        return confirmed_login

    def send_suspicious_login_message(self, request):
        session = request.session
        device_id = request.COOKIES['device_id']
        current_site = get_current_site(request)

        template_context = {
            'user': self,
            'city': get_city(session.ip),
            'country': get_country(session.ip),
            'user_agent': session.user_agent,
            'protocol': 'https' if request.is_secure() else 'http',
            'domain': current_site.domain
        }

        self.email_user(
            render_to_string('emails/suspicious_login_subject.txt', template_context),
            render_to_string('emails/suspicious_login.txt', template_context),
            html_message=(render_to_string('emails/suspicious_login.html', template_context)),
            fail_silently=True
        )
        # After sending the email confirm the previous login to prevend sending the email again
        PreviousLogins.confirm_login(self, device_id)


    @property
    def is_staff(self):
        return self.is_admin

class ResizedAvatars(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, db_index=True)
    large = models.ImageField(upload_to=unique_avatar_large_filename, null=True, blank=True)
    medium = models.ImageField(upload_to=unique_avatar_medium_filename, null=True, blank=True)
    small = models.ImageField(upload_to=unique_avatar_small_filename, null=True, blank=True)
    tiny = models.ImageField(upload_to=unique_avatar_tiny_filename, null=True, blank=True)
    topbar = models.ImageField(upload_to=unique_avatar_topbar_filename, null=True, blank=True)

    def make_avatars(user, master_avatar):
        try:
            self = ResizedAvatars.objects.get(user=user)
        except ResizedAvatars.DoesNotExist:
            self = ResizedAvatars.objects.create(user=user)

        try:
            avatar = Image.open(master_avatar)
        except:
            return

        if avatar.size[0] > avatar.size[1]:
            left = (avatar.size[0] - avatar.size[1]) / 2
            top = 0
            right = avatar.size[0] - left
            bottom = avatar.size[1]
        else:
            left = 0
            top = (avatar.size[1] - avatar.size[0]) / 2
            right = avatar.size[0]
            bottom = avatar.size[1] - top

        avatar_square = avatar.crop((left, top, right, bottom))

        ext = master_avatar.name.split('.')[-1]

        self.large = self.resize_avatar(avatar_square, 'large', ext)
        self.medium = self.resize_avatar(avatar_square, 'medium', ext)
        self.small = self.resize_avatar(avatar_square, 'small', ext)
        self.tiny = self.resize_avatar(avatar_square, 'tiny', ext)
        self.topbar = self.resize_avatar(avatar_square, 'topbar', ext)

        self.save()

    def resize_avatar(self, avatar_square, size, ext):
        avatar_sizes = {'large': [200,200],
                        'medium': [100,100],
                        'small':  [40,40],
                        'tiny': [25,25],
                        'topbar': [16,16]
        }
        new_size = avatar_sizes.get(size)
        if not new_size:
            new_size = avatar_sizes.get('medium')

        filename = "%s.%s" % (size, ext)

        a_stream = BytesIO()

        #Resize/modify the image
        resized_avatar = avatar_square.resize(new_size, Image.ANTIALIAS)

        #after modifications, save it to the output
        resized_avatar.save(a_stream, format='JPEG')
        a_stream.seek(0)

        #change the imagefield value to be the newley modifed image value
        return InMemoryUploadedFile(a_stream,
                                    'ImageField', 
                                    unique_avatar_filepath(self.user, filename), 
                                    'image/jpeg', 
                                    sys.getsizeof(a_stream), 
                                    None)

class PreviousLogins(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, db_index=True, related_name='previous_logins')
    device_id = models.CharField(max_length=40, editable=False, null=True, db_index=True)
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP')
    user_agent = models.CharField(null=True, blank=True, max_length=200)
    city = models.CharField(null=True, blank=True, max_length=100)
    country = models.CharField(null=True, blank=True, max_length=100)
    latitude = models.DecimalField(max_digits=5, decimal_places=3, null=True)
    longitude = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    last_login_date = models.DateTimeField(default=timezone.now)
    confirmed_login = models.BooleanField(default=False)

    def add_known_login(request, user):
        session = request.session
        device_id = request.COOKIES['device_id']

        lat_lon = get_lat_lon(session.ip)
        try:
            latitude = lat_lon[0]
            longitude = lat_lon[1]
        except:
            latitude = None
            longitude = None

        login = PreviousLogins.objects.create(
            user = user,
            device_id =  device_id,
            ip = session.ip,
            user_agent = get_device(session.user_agent),
            city = get_city(session.ip),
            country = get_country(session.ip),
            latitude = latitude,
            longitude = longitude,
         )
        login.save()

    def update_previous_login(self, request):
        session = request.session

        try:
            self.last_login_date = timezone.now()
            self.ip = session.ip
            self.user_agent = get_device(session.user_agent)
            self.city = get_city(session.ip)
            self.country = get_country(session.ip)
            self.lat_lon = get_lat_lon(session.ip)
            self.save()
        except:
            pass

    def confirm_login(user, device_id):
        try:
            self = PreviousLogins.objects.get(
                user=user,
                device_id=device_id
            )
            self.confirmed_login = True
            self.save()

            return True

        except PreviousLogins.DoesNotExist:
            return False

class PleioPartnerSite(models.Model):
    partner_site_url = models.URLField(null=False, db_index=True)
    partner_site_name = models.CharField(null=False, max_length=200)
    partner_site_logo_url = models.URLField(null=False)


class EventLog(models.Model):
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP')
    event_type = models.CharField(null=True, blank=True, max_length=100)
    event_time = models.DateTimeField(default=timezone.now)

    def add_event(request, event_type):
        session = request.session

        event = EventLog.objects.create(
            ip = session.ip,
            event_type = event_type,
         )
        event.save()

    def reCAPTCHA_needed(request):
        time_threshold = timezone.now() - timedelta(minutes=settings.RECAPTCHA_MINUTES_THRESHOLD)
        session = request.session
        events = EventLog.objects.filter(
	        ip = session.ip,
        	event_time__gt=time_threshold, 
	        event_type = 'invalid login'
        )

        return (events.count() > settings.RECAPTCHA_NUMBER_INVALID_LOGINS)

class PleioLegalText(models.Model):
    page_name = models.CharField(null=False, max_length=50, db_index=True)
    language_code = models.CharField(null=False, max_length=10)
    legal_text = models.TextField(null=False)

    def __str__(self):
        return self.page_name + " " + self.language_code

    def get_legal_text(request, page_name, language_code=None):
        page_found = True
        if not page_name:
            page_found = False

        if not language_code:
            language_code = get_language()

        try:
            row = PleioLegalText.objects.get(page_name=page_name, language_code=language_code)
        except PleioLegalText.DoesNotExist:
            try: 
                row = PleioLegalText.objects.filter(page_name=page_name)[0]
            except IndexError:
                page_found = False

        if page_found:
            result = mark_safe(row.legal_text)
        else:
            result = _("<H1>Page under construction</H1>")

        return mark_safe(result)