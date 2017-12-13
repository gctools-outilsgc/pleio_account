"""
Registration form validation tests using emailvalidator app
"""
from django.test import TestCase
from .validator import is_email_valid


class EmailValidatorAnyTestCase(TestCase):
    """
    Run tests when the database allows any email address
    """
    fixtures = ['emailvalidator-any.json']

    def test_valid(self):
        """
        Test email addresses that should be valid
        """
        self.assertIs(is_email_valid("anyone@anywhere.net"), True)


class EmailValidatorGoCTestCase(TestCase):
    """
    Run tests when the database only accepts GoC addresses
    """
    fixtures = ['emailvalidator-goc.json']

    def test_valid(self):
        """
        Test email addresses that should be valid
        """
        self.assertIs(is_email_valid("someone@canada.ca"), True)
        self.assertIs(is_email_valid("someone@dept.gc.ca"), True)

    def test_invalid(self):
        """
        Test email addresses that should be invalid
        """
        self.assertIs(is_email_valid("anyone@anywhere.net"), False)
        self.assertIs(is_email_valid("invalid@gc.ca"), False)
        self.assertIs(is_email_valid("invalid@dept.gc.g.ca"), False)
