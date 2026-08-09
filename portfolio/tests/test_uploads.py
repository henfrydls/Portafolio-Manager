"""Tests for upload-path helpers (issue #61)."""
from django.test import SimpleTestCase

from portfolio.utils.uploads import UUIDUploadTo


class UUIDUploadToTest(SimpleTestCase):

    def test_renames_to_uuid_keeping_extension(self):
        path = UUIDUploadTo('blog')(None, 'My Screenshot (2).PNG')
        self.assertRegex(path, r'^blog/[0-9a-f]{32}\.png$')

    def test_uses_the_configured_subdir(self):
        path = UUIDUploadTo('projects')(None, 'photo.jpg')
        self.assertTrue(path.startswith('projects/'))

    def test_names_are_unique_across_calls(self):
        upload_to = UUIDUploadTo('blog')
        self.assertNotEqual(upload_to(None, 'a.png'), upload_to(None, 'a.png'))

    def test_handles_filenames_without_extension(self):
        path = UUIDUploadTo('blog')(None, 'noextension')
        self.assertRegex(path, r'^blog/[0-9a-f]{32}$')

    def test_deconstructs_for_migrations(self):
        path, args, kwargs = UUIDUploadTo('blog').deconstruct()
        self.assertEqual(path, 'portfolio.utils.uploads.UUIDUploadTo')
        self.assertEqual(args, ('blog',))
