from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase
from django.contrib import auth
from django.core import mail, signing
from django.conf import settings
from django.test.client import RequestFactory
from core.models import User, PreviousLogins
from core.middleware import DeviceIdMiddleware


class PreviousLoginTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(name="John", email="john@user.com", password="GkCyKt6iWJVi")
        self.superuser = User.objects.create_superuser(name="John", email="john@superuser.com", password="LZwHZucJj9JD")

        self.factory = RequestFactory()

    def test_send_email_suspicious_login(self):
        """ Test  sending an email after a suspicious login"""
        request = self.factory.get("/")
        request.user = self.user

        middleware = SessionMiddleware()
        middleware.process_request(request)

        request.session.ip = "8.247.18.183" #www.ziggo.nl an existing ip address
        request.session.user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/62.0.3202.75 Chrome/62.0.3202.75 Safari/537.36"

        device_id = "yj9zaceo1v6i6uw4hr0k2h8qs11zvjgd"
        request.COOKIES['device_id'] = device_id

        result = self.user.check_users_previous_logins(request)
        self.assertIs(result, False)#no confirmed previous login found, so an email has been sent

        acceptation_token = signing.dumps(obj=(device_id,self.user.email))
        PreviousLogins.accept_previous_logins(request, acceptation_token)

        result = self.user.check_users_previous_logins(request)
        self.assertIs(result, True)#confirmed previous login found, no email has been sent

    def test_accept_previous_login(self):
        """ Test accepting a previous login"""
        request = self.factory.get("/")
        request.user = self.user

        middleware = SessionMiddleware()
        middleware.process_request(request)

        request.session.ip = "8.247.18.183" #www.ziggo.nl an existing ip address
        request.session.user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/62.0.3202.75 Chrome/62.0.3202.75 Safari/537.36"

        device_id = "v76iswyyp0ejhfdai654kzcrh32owo9y"
        request.COOKIES['device_id'] = device_id

        self.previouslogin = PreviousLogins.add_known_login(request, self.user)

        acceptation_token = signing.dumps(obj=(device_id,self.user.email))
        PreviousLogins.accept_previous_logins(request, acceptation_token)

        previouslogin = PreviousLogins.objects.get(device_id=device_id)
        result = previouslogin.confirmed_login
        self.assertIs(result, True)




