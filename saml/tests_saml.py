from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase
from django.contrib import auth
from django.core import mail, signing
from django.conf import settings
from django.test.client import RequestFactory
from core.models import User
from core.middleware import DeviceIdMiddleware
from saml.models import IdentityProvider, ExternalId
from saml.views import check_externalid, connect


class SamlTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(name="John", email="john@user.com", password="GkCyKt6iWJVi")
        self.superuser = User.objects.create_superuser(name="John", email="john@superuser.com", password="LZwHZucJj9JD")
        self.idp = IdentityProvider.objects.create(
            shortname = "idp1",
            displayname = "idp organisation",
            entityId =  "http://localhost:8480/simplesaml/saml2/idp/metadata.php"
        )

        self.factory = RequestFactory()

    def test_check_externalid(self):
        '''
        Saml user who is logging in first time does not have a connected concierge user
        '''
        request = self.factory.get("/")
        request.session = {}
        request.session["idp"] = "idp1"
        request.session["samlUserdata"] =  {'uid': ["1"], 'email': ["johnsaml@user.com"]}

        extid = check_externalid(request, shortname=self.idp.shortname, externalid="johnsaml@user.com")
        self.assertIs(extid, None)# No externalid exists atm

    def test_connect_new_samluser(self):
        '''
        Saml user who is logging in first time does not have a connected concierge user
        A concierge user will be created based on saml user data and connected with saml user
        '''
        request = self.factory.get("/")
        request.session = {}
        request.session["idp"] = "idp1"
        request.session["samlUserdata"] =  {'uid': ["1"], 'email': ["johnsaml@user.com"]}

        result = check_externalid(request, shortname=self.idp.shortname, externalid="johnsaml@user.com")
        self.assertIs(result, None)# No externalid exists atm

        extid = connect(request, user_email=None)# Do not connect with existing user
        self.assertEqual(extid.externalid, "johnsaml@user.com")# An externalid exists atm
        self.assertEqual(extid.userid, User.objects.get(email="johnsaml@user.com"))# Externalid exists with new user

        self.assertEqual(len(mail.outbox), 1)# An email to request a new password has been sent
        self.assertEqual(mail.outbox[0].subject, "Please set your new password")# Verifying email subject
        mail.outbox = []# Empty the test outbox


    def test_connect_new_samluser_with_existing_user(self):
        '''
        Saml user who is logging in first time does not have a connected concierge user
        An existing concierge user will be connected with saml user
        '''
        request = self.factory.get("/")
        request.session = {}
        request.session["idp"] = "idp1"
        request.session["samlUserdata"] =  {'uid': ["1"], 'email': ["johnsaml@user.com"]}

        result = check_externalid(request, shortname=self.idp.shortname, externalid="johnsaml@user.com")
        self.assertIs(result, None)# No externalid exists atm

        extid = connect(request, user_email="john@user.com")# Connect with existing user
        self.assertEqual(extid.externalid, "johnsaml@user.com")# An externalid exists atm
        self.assertEqual(extid.userid, User.objects.get(email="john@user.com"))# Externalid exists existing user

        self.assertEqual(len(mail.outbox), 0)# No email to request a new password has been sent
        mail.outbox = []# Empty the test outbox
        
