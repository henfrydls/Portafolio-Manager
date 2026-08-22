"""
Tests for language detection, the language switcher and its visibility.

Covers issue #115: /es/ URLs returned 404 on a cold visit and the browser's
preferred language was ignored, so Spanish content was unreachable.
"""
from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.utils import timezone, translation

from portfolio.models import (
    BlogPost, Category, Project, ProjectType, SiteConfiguration
)
from portfolio.tests.test_views_public import create_test_profile
from django.contrib.auth import get_user_model

User = get_user_model()

SWITCHER_MARKER = 'id="portfolio-lang-switcher"'
SPANISH_HEADER = 'es-DO,es;q=0.9,en;q=0.8'
ENGLISH_HEADER = 'en-US,en;q=0.9'


def middleware_like_production():
    """config.settings.test drops SiteLanguageMiddleware, so language behaviour
    was never exercised. Put it back where production has it: right after
    LocaleMiddleware, which is the ordering the whole design depends on."""
    middleware = list(settings.MIDDLEWARE)
    target = 'portfolio.middleware.SiteLanguageMiddleware'
    if target not in middleware:
        locale_index = middleware.index('django.middleware.locale.LocaleMiddleware')
        middleware.insert(locale_index + 1, target)
    return middleware


@override_settings(MIDDLEWARE=middleware_like_production())
class BasePublicPagesTest(TestCase):
    """Builds the minimum public content needed to render every public page."""

    def setUp(self):
        self.client = Client()
        self.profile = create_test_profile()
        translation.activate('en')

        # A superuser must exist or InitialSetupRedirectMiddleware hijacks every request
        User.objects.create_superuser(
            username='admin', email='admin@example.com', password='testpass123'
        )

        self.project_type, _ = ProjectType.objects.get_or_create(slug='web-app')
        self.project_type.set_current_language('en')
        self.project_type.name = "Web Application"
        self.project_type.description = "Web apps"
        self.project_type.save()

        self.project = Project()
        self.project.set_current_language('en')
        self.project.title = "Test Project"
        self.project.description = "Detailed project description"
        self.project.project_type_obj = self.project_type
        self.project.visibility = 'public'
        self.project.save()

        self.category, _ = Category.objects.get_or_create(slug='idea')
        self.category.set_current_language('en')
        self.category.name = "Idea"
        self.category.save()

        self.post = BlogPost()
        self.post.set_current_language('en')
        self.post.title = "Test Post"
        self.post.content = "Post body"
        self.post.excerpt = "Post excerpt"
        self.post.category = self.category
        self.post.status = 'published'
        self.post.publish_date = timezone.now()
        self.post.save()


class LanguageSwitcherVisibilityTest(BasePublicPagesTest):
    """The switcher must be reachable from every public page, not a hand-kept path list."""

    def test_switcher_on_home(self):
        self.assertContains(self.client.get('/'), SWITCHER_MARKER)

    def test_switcher_on_blog_list(self):
        self.assertContains(self.client.get(reverse('portfolio:post-list')), SWITCHER_MARKER)

    def test_switcher_on_blog_detail(self):
        url = reverse('portfolio:post-detail', kwargs={'slug': self.post.slug})
        self.assertContains(self.client.get(url), SWITCHER_MARKER)

    def test_switcher_on_resume(self):
        self.assertContains(self.client.get(reverse('portfolio:resume')), SWITCHER_MARKER)

    def test_switcher_on_project_detail(self):
        """Regression: project pages were missing from the path whitelist."""
        url = reverse('portfolio:project-detail', kwargs={'slug': self.project.slug})
        self.assertContains(self.client.get(url), SWITCHER_MARKER)

    def test_hamburger_on_project_detail(self):
        """The same whitelist also dropped the mobile menu button."""
        url = reverse('portfolio:project-detail', kwargs={'slug': self.project.slug})
        self.assertContains(self.client.get(url), 'id="mobileMenuToggle"')


class SpanishUrlTest(BasePublicPagesTest):
    """/es/ URLs must work for a first-time visitor, with no session warm-up."""

    def test_es_home_serves_spanish_on_cold_visit(self):
        response = self.client.get('/es/', headers={'accept-language': ENGLISH_HEADER})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('Content-Language'), 'es')

    def test_es_blog_list_on_cold_visit(self):
        response = self.client.get('/es/posts/', headers={'accept-language': ENGLISH_HEADER})
        self.assertEqual(response.status_code, 200)

    def test_es_post_detail_on_cold_visit(self):
        response = self.client.get(
            f'/es/post/{self.post.slug}/', headers={'accept-language': ENGLISH_HEADER}
        )
        self.assertEqual(response.status_code, 200)


class BrowserLanguageDetectionTest(BasePublicPagesTest):
    """A Spanish browser should land on the Spanish URL, keeping one URL per language."""

    def test_spanish_browser_is_redirected_to_es(self):
        response = self.client.get('/', headers={'accept-language': SPANISH_HEADER})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/es/')

    def test_spanish_browser_redirect_keeps_path_and_query(self):
        response = self.client.get(
            '/posts/?category=idea', headers={'accept-language': SPANISH_HEADER}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/es/posts/?category=idea')

    def test_english_browser_is_not_redirected(self):
        response = self.client.get('/', headers={'accept-language': ENGLISH_HEADER})
        self.assertEqual(response.status_code, 200)

    def test_unsupported_language_falls_back_to_english(self):
        response = self.client.get('/', headers={'accept-language': 'de-DE,de;q=0.9'})
        self.assertEqual(response.status_code, 200)

    def test_manual_choice_beats_browser_language(self):
        """Someone who picked English keeps English even on a Spanish browser."""
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = 'en'
        response = self.client.get('/', headers={'accept-language': SPANISH_HEADER})
        self.assertEqual(response.status_code, 200)

    def test_spanish_cookie_redirects_to_es(self):
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = 'es'
        response = self.client.get('/', headers={'accept-language': ENGLISH_HEADER})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/es/')

    def test_no_redirect_loop_on_es_urls(self):
        response = self.client.get('/es/', headers={'accept-language': SPANISH_HEADER})
        self.assertEqual(response.status_code, 200)

    def test_post_requests_are_never_redirected(self):
        """Redirecting a POST would silently drop the payload."""
        response = self.client.post(
            '/', {'name': 'x'}, headers={'accept-language': SPANISH_HEADER}
        )
        self.assertNotEqual(response.status_code, 302)

    def test_sitemap_is_not_redirected(self):
        response = self.client.get('/sitemap.xml', headers={'accept-language': SPANISH_HEADER})
        self.assertEqual(response.status_code, 200)

    def test_admin_area_is_not_redirected(self):
        self.client.force_login(User.objects.get(username='admin'))
        response = self.client.get('/dashboard/', headers={'accept-language': SPANISH_HEADER})
        self.assertNotEqual(response.status_code, 302)


class SetLanguageViewTest(BasePublicPagesTest):
    """The switcher must persist the choice in the language cookie, not only the session."""

    def test_choosing_spanish_sets_the_language_cookie(self):
        response = self.client.post(reverse('set_language'), {'language': 'es', 'next': '/'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/es/')
        self.assertEqual(response.cookies[settings.LANGUAGE_COOKIE_NAME].value, 'es')

    def test_choosing_english_sets_the_language_cookie(self):
        response = self.client.post(reverse('set_language'), {'language': 'en', 'next': '/es/'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')
        self.assertEqual(response.cookies[settings.LANGUAGE_COOKIE_NAME].value, 'en')

    def test_cookie_outlives_the_session(self):
        response = self.client.post(reverse('set_language'), {'language': 'es', 'next': '/'})
        cookie = response.cookies[settings.LANGUAGE_COOKIE_NAME]
        self.assertGreater(int(cookie['max-age']), settings.SESSION_COOKIE_AGE)

    def test_unsupported_language_is_rejected(self):
        response = self.client.post(reverse('set_language'), {'language': 'de', 'next': '/'})
        self.assertEqual(response['Location'], '/')
        self.assertNotEqual(
            response.cookies.get(settings.LANGUAGE_COOKIE_NAME) and
            response.cookies[settings.LANGUAGE_COOKIE_NAME].value, 'de'
        )

    def test_choice_survives_the_next_request(self):
        self.client.post(reverse('set_language'), {'language': 'es', 'next': '/'})
        response = self.client.get('/', headers={'accept-language': ENGLISH_HEADER})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/es/')
