"""
Django admin related configuration for the emailvalidator app
"""
from django.contrib import admin
from .models import EmailRegExValidator, EmailDomainGroup


class EmailRegExValidatorInline(admin.TabularInline):
    """
    Django admin tabular display of regex patterns
    """
    model = EmailRegExValidator
    list_display = ('regex',)


class EmailDomainGroupAdmin(admin.ModelAdmin):
    """
    Django admin display of domain groups with associated regex patterns
    """
    list_display = ('name', 'get_regexes',)

    def get_regexes(self, obj):
        """
        Return list of regex patterns within the specified group
        """
        return [r.regex for r in
                EmailRegExValidator.objects.filter(group=obj)]

    get_regexes.short_description = "Regular Expressions"
    inlines = [
        EmailRegExValidatorInline,
    ]

admin.site.register(EmailDomainGroup, EmailDomainGroupAdmin)
