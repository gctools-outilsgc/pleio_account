from django.core.management.base import BaseCommand, CommandError
from core.models import User
from migrate_from_legacy.views import migrate

class Command(BaseCommand):
    help = 'Migrates pleio_legacy users to concierge users'

    #def add_arguments(self, parser):
    #    parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        migrate(options.get('verbosity'))
        #users = User.objects.all()
        #for user in users:
        #    self.stdout.write(self.style.SUCCESS(user.email))