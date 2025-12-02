from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Load specific fixture'

    def handle(self, *args, **options):
        abs_path = settings.BASE_DIR / 'tests' / 'db.json'
        call_command('dumpdata', '-a', '-o', str(abs_path))
