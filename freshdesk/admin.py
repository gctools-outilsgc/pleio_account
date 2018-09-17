from django.contrib import admin

# Register your models here.
from .models import Configuration

class FreshdeskAdmin(admin.ModelAdmin):
    list_display = ('url', 'default')
    list_display_links = ('url', 'default')
    search_fields = ('url', 'url')
    list_per_page = 25

admin.site.register(Configuration, FreshdeskAdmin)