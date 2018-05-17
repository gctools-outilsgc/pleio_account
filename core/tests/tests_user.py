from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase
from django.contrib import auth
from django.core import mail, signing
from django.conf import settings
from django.test.client import RequestFactory
from core.models import User
from core.middleware import DeviceIdMiddleware


class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(name="John", email="john@user.com", password="GkCyKt6iWJVi")

        self.superuser = User.objects.create_superuser(name="John", email="john@superuser.com", password="LZwHZucJj9JD")

        self.factory = RequestFactory()

    def test_generated_username(self):
        """ Make sure a correct unique username is generated for each user """
        self.assertEqual(self.user.username, "john")
        self.assertEqual(self.superuser.username, "john1")

    def test_normal_user_is_inactive_when_created(self):
        """ Make sure a (normal) user is in inactive state when being created """
        self.assertIs(self.user.is_active, False)

    def test_superuser_is_active_when_created(self):
        """ Make sure a superuser is in active state when being created """
        self.assertIs(self.superuser.is_active, True)

    def test_login_with_email(self):
        """ Make sure a user can login with email and password """
        invalid_login = auth.authenticate(username="john@superuser.com", password="asdf")
        valid_login = auth.authenticate(username="john@superuser.com", password="LZwHZucJj9JD")
        self.assertEqual(invalid_login, None)
        self.assertEqual(valid_login, self.superuser)

    def test_send_activation_token(self):
        """ Test sending an email after user has registered"""
        self.user.send_activation_token()
        self.assertEqual(len(mail.outbox), 1)# An email has been sent
        mail.outbox = []# Empty the test outbox

    def test_send_change_email_activation_token(self):
        """ Test sending an email after user has changed his email address"""
        self.user.new_email="newjohn@user.com"
        self.user.send_change_email_activation_token()
        self.assertEqual(len(mail.outbox), 1)# An email has been sent
        mail.outbox = []# Empty the test outbox

    def test_send_set_password_activation_token(self):
        """ Test sending an email after user has required a password"""
        self.user.send_set_password_activation_token()
        self.assertEqual(len(mail.outbox), 1)# An email has been sent
        mail.outbox = []# Empty the test outbox

    def test_account_activation(self):
        """ Test an account can be activated and login by using the activation token """
        request = self.factory.get("/")
        request.user = self.user

        middleware = SessionMiddleware()
        middleware.process_request(request)

        activation_token = signing.dumps(obj=self.user.email)
        self.user.activate_user(activation_token)

        self.user.refresh_from_db()

        self.assertIs(self.user.is_active, True)
        self.assertEqual(request.user, self.user)
