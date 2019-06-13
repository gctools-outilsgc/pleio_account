from django.core.management.base import BaseCommand
from core.models import User
from core.service_mesh import service_mesh_message
import json

class Command(BaseCommand):
    help = 'Seeds Profiles as a Service with all active accounts'

    def handle(self, *args, **kwargs):
        for user in User.objects.filter(is_active=True):

            service_mesh_message('user.new', json.dumps({
                'gcID': str(user.id),
                'name': user.name,
                'email': user.email
            }))


