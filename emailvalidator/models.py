"""
Model definitions for emailvalidator
"""
from django.db import models


class EmailDomainGroup(models.Model):
    """
    Naming of groups of regex patterns
    """
    name = models.CharField(max_length=255)


class EmailRegExValidator(models.Model):
    """
    Regex patterns
    """
    regex = models.CharField(max_length=100)
    group = models.ForeignKey(EmailDomainGroup)
