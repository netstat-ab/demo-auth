__all__ = ['TEST_DB_FIXTURE_PATH']

from django.conf import settings

TEST_DB_FIXTURE_PATH = settings.BASE_DIR / 'tests' / 'db.json'
