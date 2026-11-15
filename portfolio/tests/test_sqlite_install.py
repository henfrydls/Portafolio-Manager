"""
A fresh install on SQLite, the database of the README quick start.

Several data migrations and Profile.get_solo() wrote raw SQL for the
PostgreSQL schema (legacy columns, NOW(), DROP COLUMN IF EXISTS), so
`migrate` stopped at 0031 on SQLite and a new user never got a site.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from django.conf import settings
from django.db import connection
from django.test import SimpleTestCase, TestCase

from portfolio.migration_utils import table_columns

SMOKE_CHECK = """
from django.test import Client
from portfolio.models import Category, KnowledgeBase, Profile, ProjectType
Profile.get_solo()
assert KnowledgeBase.objects.exists() and Category.objects.exists() and ProjectType.objects.exists()
client = Client(HTTP_HOST='localhost')
print('setup', client.get('/').status_code)
"""


class SqliteInstallTest(SimpleTestCase):

    def run_manage(self, database, *args):
        env = {
            **os.environ,
            'DJANGO_SETTINGS_MODULE': 'config.settings.development',
            'DATABASE_URL': f'sqlite:///{database}',
        }
        return subprocess.run(
            [sys.executable, 'manage.py', *args],
            cwd=settings.BASE_DIR, env=env, capture_output=True, text=True, timeout=300,
        )

    def test_migrate_and_first_request(self):
        with tempfile.TemporaryDirectory() as folder:
            database = Path(folder) / 'install.sqlite3'

            migrate = self.run_manage(database, 'migrate', '--verbosity', '0')
            self.assertEqual(migrate.returncode, 0, migrate.stderr[-2000:])

            # The model and the database agree: nothing left to migrate
            check = self.run_manage(database, 'migrate', '--check')
            self.assertEqual(check.returncode, 0, check.stderr[-2000:])

            # Default content was created and the site answers (with no
            # superuser yet, the home page redirects to the setup wizard)
            smoke = self.run_manage(database, 'shell', '-c', SMOKE_CHECK)
            self.assertEqual(smoke.returncode, 0, smoke.stderr[-2000:])
            self.assertIn('setup 302', smoke.stdout)


class MigrationUtilsTest(TestCase):

    def test_table_columns(self):
        columns = table_columns(connection, 'portfolio_category')
        self.assertLessEqual({'id', 'slug', 'is_active', 'order'}, columns)
        self.assertNotIn('no_such_column', columns)
