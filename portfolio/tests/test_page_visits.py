"""
Tests for which requests PageVisitMiddleware records.

The tracked paths were written without a language prefix, so no visit to a
/es/ page was ever counted and the dashboard showed English traffic only.
"""
from portfolio.models import PageVisit
from portfolio.tests.test_i18n_language import BasePublicPagesTest

BROWSER = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36'


class PageVisitLanguagePrefixTest(BasePublicPagesTest):

    def visit(self, path, user_agent=BROWSER):
        return self.client.get(path, headers={'user-agent': user_agent, 'accept-language': 'en'})

    def recorded(self):
        return list(PageVisit.objects.order_by('id').values_list('page_url', flat=True))

    def test_english_pages_are_recorded(self):
        for path in ('/', '/posts/', '/resume/', f'/post/{self.post.slug}/',
                     f'/project/{self.project.slug}/'):
            self.visit(path)
        self.assertEqual(len(self.recorded()), 5)

    def test_spanish_pages_are_recorded_with_their_own_url(self):
        paths = ['/es/', '/es/posts/', '/es/resume/', f'/es/post/{self.post.slug}/',
                 f'/es/project/{self.project.slug}/']
        for path in paths:
            self.assertEqual(self.visit(path).status_code, 200)
        self.assertEqual(self.recorded(), paths)

    def test_spanish_and_english_versions_share_the_page_title(self):
        self.visit('/resume/')
        self.visit('/es/resume/')
        titles = set(PageVisit.objects.values_list('page_title', flat=True))
        self.assertEqual(len(titles), 1)

    def test_private_pages_are_not_recorded_in_any_language(self):
        for path in ('/login/', '/es/login/', '/dashboard/', '/es/dashboard/'):
            self.visit(path)
        self.assertEqual(self.recorded(), [])

    def test_a_path_that_only_starts_like_a_language_code_is_left_alone(self):
        self.visit('/essay/')
        self.assertEqual(self.recorded(), [])

    def test_bots_are_not_recorded_on_spanish_pages(self):
        self.visit('/es/', user_agent='Mozilla/5.0 (compatible; Googlebot/2.1)')
        self.assertEqual(self.recorded(), [])
