from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Flushes all data from database and reloads it'

    def handle(self, *args, **options):
        prompt = 'All data from database will be dropped and then reloaded. Type \'yes\' to confirm: '
        if input(prompt) != 'yes':
            print('Operation canceled.')
            return

        call_command('flush', '--noinput')
        for app in 'accounts', 'auth', 'contenttypes':
            call_command('migrate', app, 'zero')
        call_command('migrate')
        call_command('loaddata', str(settings.BASE_DIR / 'tests' / 'db.json'))
