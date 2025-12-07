from django.core.management import call_command
from django.core.management.base import BaseCommand

from ._const import TEST_DB_FIXTURE_PATH


class Command(BaseCommand):
    help = 'Load specific fixture'

    def handle(self, *args, **options):
        call_command('dumpdata', '-a', '-o', str(TEST_DB_FIXTURE_PATH))

