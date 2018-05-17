"""
Registration form validation tests using emailvalidator app
"""
from django.test import TestCase
from .validator import is_email_valid, get_email_groups, is_email_in_group


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


class EmailValidatorGroupMatchTestCase(TestCase):
    """
    Run tests to determine group membership
    """
    fixtures = ['emailvalidator-any.json', 'emailvalidator-goc.json']

    def test_group_count(self):
        """
        Test if returned group count matches expectations
        """
        groups = get_email_groups("testing@anywher.net")
        self.assertIs(len(groups), 1)

        groups = get_email_groups("someone@canada.ca")
        self.assertIs(len(groups), 2)

    def test_group_array(self):
        """
        Test if returned group array is correct
        """
        groups = get_email_groups("testing@anywhere.net")
        self.assertEqual(groups[0].name, 'All')

        groups = get_email_groups("someone@canada.ca")
        for group in groups:
            self.assertIn(group.name, ['Government of Canada', 'All'])

    def test_group_membership(self):
        """
        Test group membership functions
        """
        self.assertIs(is_email_in_group("someone@canada.ca", "All"), True)
        self.assertIs(is_email_in_group("someone@canada.ca", "Fake"), False)
        self.assertIs(is_email_in_group(
            "someone@canada.ca",
            "Government of Canada"
        ), True)
        self.assertIs(is_email_in_group(
            "someone@anywhere.net",
            "Government of Canada"
        ), False)
        self.assertIs(is_email_in_group("someone@anywhere.net", "All"), True)

