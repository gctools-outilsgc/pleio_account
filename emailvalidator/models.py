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
    name = models.CharField("Name", max_length=255)
    regex = models.CharField("Regex/domain", max_length=100)
    allow_all = models.BooleanField("Allow all from domain", default=False)
    group = models.ForeignKey(EmailDomainGroup)
