from django.contrib import admin, messages
from requestmembership.models import LimboUser
from core.models import User

def make_user(modeladmin, request, queryset):
    for limboUser in queryset:
        user = User.objects.create_user(
            name=limboUser.name,
            email=limboUser.email,
            password=limboUser.password,
            accepted_terms=True
        )

        if not user.is_active:
            user.send_activation_token(request)

    messages.add_message(request, messages.INFO, 'User has been created')
make_user.short_description = "Activate User"

class LimboUserAdmin(admin.ModelAdmin):
    actions = [make_user]

admin.site.register(LimboUser, LimboUserAdmin)
