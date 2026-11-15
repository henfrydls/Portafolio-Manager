"""
Tests for the static files configuration (issue #170).

Production and staging set STATICFILES_STORAGE, which Django 5.1 removed, so
the hashed and compressed storage they asked for was never active.
"""
import importlib
import json
import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.management import call_command
from django.test import SimpleTestCase, override_settings

from portfolio.tests.test_i18n_language import BasePublicPagesTest

MANIFEST_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


class StorageSettingsTest(SimpleTestCase):

    def test_production_and_staging_use_the_manifest_storage(self):
        for name in ('production', 'staging'):
            with self.subTest(settings=name):
                module = importlib.import_module(f'config.settings.{name}')
                self.assertEqual(module.STORAGES['staticfiles']['BACKEND'], MANIFEST_STORAGE)
                # Media uploads keep the default storage
                self.assertEqual(
                    module.STORAGES['default']['BACKEND'],
                    'django.core.files.storage.FileSystemStorage')

    def test_no_settings_module_uses_the_removed_setting(self):
        for name in ('base', 'development', 'staging', 'production', 'test'):
            with self.subTest(settings=name):
                module = importlib.import_module(f'config.settings.{name}')
                self.assertFalse(hasattr(module, 'STATICFILES_STORAGE'))
                self.assertFalse(hasattr(module, 'DEFAULT_FILE_STORAGE'))

    def test_production_does_not_serve_from_the_source_tree(self):
        # Development switches: they make WhiteNoise look files up on every
        # request instead of serving the collected, hashed copies.
        for name in ('production', 'staging'):
            with self.subTest(settings=name):
                module = importlib.import_module(f'config.settings.{name}')
                self.assertFalse(getattr(module, 'WHITENOISE_AUTOREFRESH', False))
                self.assertFalse(getattr(module, 'WHITENOISE_USE_FINDERS', False))


class ManifestStorageTest(BasePublicPagesTest):
    """Collects the real static files the way production does."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.static_root = tempfile.mkdtemp(prefix='static-manifest-')
        cls.overrides = override_settings(
            STATIC_ROOT=cls.static_root,
            STORAGES={**settings.STORAGES, 'staticfiles': {'BACKEND': MANIFEST_STORAGE}},
        )
        cls.overrides.enable()
        # A missing file referenced from a stylesheet fails here, as it
        # would when the container starts.
        call_command('collectstatic', interactive=False, verbosity=0)

    @classmethod
    def tearDownClass(cls):
        cls.overrides.disable()
        shutil.rmtree(cls.static_root, ignore_errors=True)
        super().tearDownClass()

    def test_files_get_hashed_names(self):
        manifest = json.loads((Path(self.static_root) / 'staticfiles.json').read_text())
        hashed = manifest['paths']['js/session-manager.js']
        self.assertRegex(hashed, r'^js/session-manager\.[0-9a-f]{12}\.js$')
        self.assertEqual(staticfiles_storage.url('js/session-manager.js'), f'/static/{hashed}')

    def test_compressed_copies_are_written(self):
        manifest = json.loads((Path(self.static_root) / 'staticfiles.json').read_text())
        hashed = Path(self.static_root) / manifest['paths']['js/session-manager.js']
        self.assertTrue(hashed.with_name(hashed.name + '.gz').exists())

    def test_original_names_are_kept(self):
        # Paths written by hand (manifest.json icons, the favicon redirect)
        # keep working next to the hashed copies.
        self.assertTrue((Path(self.static_root) / 'images/favicon/favicon.ico').exists())

    def test_every_static_file_is_in_the_manifest(self):
        manifest = json.loads((Path(self.static_root) / 'staticfiles.json').read_text())
        for path in ('images/favicon/favicon.ico', 'images/favicon/favicon.svg',
                     'images/favicon/site.webmanifest', 'js/session-manager.js'):
            with self.subTest(path=path):
                self.assertIsNotNone(finders.find(path))
                self.assertIn(path, manifest['paths'])

    def test_public_pages_render_with_hashed_urls(self):
        # A {% static %} pointing at a file that is not in the manifest is a
        # 500 under this storage.
        for path in ('/', '/es/', '/posts/', '/resume/'):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertRegex(
                    response.content.decode(),
                    r'/static/images/favicon/favicon\.[0-9a-f]{12}\.svg')
