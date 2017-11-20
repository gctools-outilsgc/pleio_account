from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.utils.text import slugify
from django.core import signing
from django.core.mail import send_mail
from django.contrib import admin
from django.contrib.sites.shortcuts import get_current_site
from django.db import models
from django.conf import settings
from django.template.loader import render_to_string
from .helpers import unique_filepath
from .login_session_helpers import get_city, get_country, get_device, get_lat_lon

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
    avatar = models.ImageField(upload_to=unique_filepath, null=True, blank=True)

    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['name']
    USERNAME_FIELD = 'email'

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self._get_unique_username()

        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.email

    def _get_unique_username(self):
        max_length = User._meta.get_field('username').max_length
        username = slugify(self.email.split("@")[0])
        unique_username = username[:max_length]
        i = 1

        while User.objects.filter(username=unique_username).exists():
            unique_username = '{}-{}'.format(username[:max_length - len(str(i)) - 1], i)
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
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email], **kwargs)

    def send_activation_token(self, request):
        template_context = {
            'site': get_current_site(request),
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
            'activation_token': signing.dumps(obj=self.email)
        }

        self.email_user(
            render_to_string('emails/register_subject.txt', template_context),
            render_to_string('emails/register.txt', template_context),
            html_message = (render_to_string('emails/register.html', template_context)),
            fail_silently = True
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

        template_context = {
            'site': get_current_site(request),
            'user': self.email,
            'user_agent': session.user_agent,
            'ip_address': session.ip,
            'city': get_city(session.ip),
            'country': get_country(session.ip),
            'acceptation_token': signing.dumps(obj=(device_id, self.email)),
            'pleio_logo_small': request.build_absolute_uri("/static/images/pleio_logo_small.png")
        }

        self.email_user(
            render_to_string('emails/send_suspicious_login_message_subject.txt', template_context),
            render_to_string('emails/send_suspicious_login_message.txt', template_context),
            html_message=(render_to_string('emails/send_suspicious_login_message.html', template_context)),
            fail_silently=True
        )

    @property
    def is_staff(self):
        return self.is_admin

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

    def accept_previous_logins(request, acceptation_token):
        try:
            signed_value = signing.loads(
                acceptation_token,
                max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400
            )
            device_id = signed_value[0]
            email = signed_value[1]
            user = User.objects.get(email = email)

            if device_id is None:
                return False

            self = PreviousLogins.objects.get(
                user=user,
                device_id=device_id
            )
            self.confirmed_login = True
            self.save()

            return True

        except (signing.BadSignature, PreviousLogins.DoesNotExist):
            return False

admin.site.register(User)