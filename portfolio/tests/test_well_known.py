"""
Tests for /.well-known/security.txt and /manifest.json.

security.txt shipped with "security@example.com" and an example.com
canonical, and the manifest pointed at icons that do not exist.
"""
from django.contrib.staticfiles import finders
from django.test import override_settings

from portfolio.tests.test_i18n_language import BasePublicPagesTest, SPANISH_HEADER

URL = '/.well-known/security.txt'


class SecurityTxtTest(BasePublicPagesTest):

    def test_not_served_without_a_configured_contact(self):
        with override_settings(SECURITY_CONTACT=''):
            self.assertEqual(self.client.get(URL).status_code, 404)

    @override_settings(SECURITY_CONTACT='security@portfolio.test')
    def test_email_contact(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('text/plain'))
        body = response.content.decode()
        self.assertIn('Contact: mailto:security@portfolio.test\n', body)
        self.assertIn('Canonical: http://testserver/.well-known/security.txt\n', body)
        self.assertRegex(body, r'Expires: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\n')
        self.assertIn('Preferred-Languages: en, es\n', body)
        self.assertNotIn('example.com', body)

    @override_settings(SECURITY_CONTACT='https://portfolio.test/report')
    def test_url_contact_is_used_as_is(self):
        self.assertIn('Contact: https://portfolio.test/report\n', self.client.get(URL).content.decode())

    @override_settings(SECURITY_CONTACT='security@portfolio.test')
    def test_spanish_browsers_get_the_file_not_a_redirect(self):
        response = self.client.get(URL, headers={'accept-language': SPANISH_HEADER})
        self.assertEqual(response.status_code, 200)


class ManifestTest(BasePublicPagesTest):

    def test_icons_exist(self):
        manifest = self.client.get('/manifest.json').json()
        self.assertEqual(len(manifest['icons']), 2)
        for icon in manifest['icons']:
            with self.subTest(icon=icon['src']):
                self.assertTrue(icon['src'].startswith('/static/'))
                self.assertIsNotNone(finders.find(icon['src'][len('/static/'):]))
