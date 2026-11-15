"""
Tests for the language hint.

A visitor who opens a page in one language with a browser set to the other
(a shared /es/ link opened by an English reader, for instance) gets a small
notice, written in their language, pointing to that version. Whether it is
shown is decided in the browser (it depends on the browser's language and
on localStorage); these tests cover what the server sends.
"""
import re

from django.conf import settings
from django.urls import reverse

from portfolio.tests.test_i18n_language import BasePublicPagesTest, User


def hint_markup(html):
    match = re.search(r'<aside id="portfolio-lang-hint".*?</aside>', html, re.S)
    return match.group(0) if match else None


class LanguageHintTest(BasePublicPagesTest):

    def hint(self, path):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        return hint_markup(response.content.decode())

    def test_english_page_offers_spanish_in_spanish(self):
        hint = self.hint('/')
        self.assertIn('data-hint-language="es"', hint)
        self.assertIn('lang="es"', hint)
        self.assertIn('Disponible en español', hint)
        self.assertIn('name="language" type="hidden" value="es"', hint)

    def test_spanish_page_offers_english_in_english(self):
        hint = self.hint('/es/')
        self.assertIn('data-hint-language="en"', hint)
        self.assertIn('lang="en"', hint)
        self.assertIn('Also in English', hint)
        self.assertIn('name="language" type="hidden" value="en"', hint)

    def test_hint_is_hidden_until_the_browser_decides(self):
        for path in ('/', '/es/'):
            with self.subTest(path=path):
                opening_tag = self.hint(path).split('>', 1)[0]
                self.assertRegex(opening_tag, r'\shidden$')

    def test_hint_returns_to_the_page_being_read(self):
        hint = self.hint('/es/posts/?page=1')
        self.assertIn('name="next" type="hidden" value="/es/posts/?page=1"', hint)

    def test_hint_is_on_every_public_page(self):
        for path in ('/', '/posts/', '/resume/', '/es/', '/es/posts/', '/es/resume/'):
            with self.subTest(path=path):
                self.assertIsNotNone(self.hint(path))

    def test_using_the_hint_switches_the_language(self):
        response = self.client.post(
            reverse('set_language'), {'language': 'es', 'next': '/posts/'})
        self.assertRedirects(response, '/es/posts/', fetch_redirect_response=False)

    def test_no_hint_once_the_visitor_chose_a_language(self):
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = 'es'
        for path in ('/es/', '/es/posts/'):
            with self.subTest(path=path):
                self.assertIsNone(self.hint(path))

    def test_dashboard_has_no_hint(self):
        self.client.force_login(User.objects.get(username='admin'))
        response = self.client.get(reverse('portfolio:admin-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(hint_markup(response.content.decode()))
