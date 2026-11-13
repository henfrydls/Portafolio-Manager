"""
Tests for the signals that tell search engines the English and Spanish
versions of a page are the same content (issue #141): canonical, hreflang,
a sitemap that lists both languages, and descriptions cut on a word boundary.
"""
import re

from django.test import SimpleTestCase
from django.urls import reverse
from django.utils import timezone, translation

from portfolio.models import BlogPost, Category
from portfolio.tests.test_i18n_language import BasePublicPagesTest
from portfolio.utils.seo import SEOGenerator

HOST = 'http://testserver'


def head_links(html):
    """{(rel, hreflang or None): href} for every <link> in the page."""
    links = {}
    for tag in re.findall(r'<link\b[^>]*>', html):
        rel = re.search(r'rel="([^"]*)"', tag)
        href = re.search(r'href="([^"]*)"', tag)
        hreflang = re.search(r'hreflang="([^"]*)"', tag)
        if rel and href:
            links[(rel.group(1), hreflang.group(1) if hreflang else None)] = href.group(1)
    return links


class CanonicalAndHreflangTest(BasePublicPagesTest):

    def pages(self):
        return {
            'home': '/',
            'blog list': '/posts/',
            'post': f'/post/{self.post.slug}/',
            'project': f'/project/{self.project.slug}/',
            'resume': '/resume/',
        }

    def links_for(self, path, language):
        prefix = '/es' if language == 'es' else ''
        response = self.client.get(prefix + path, headers={'accept-language': 'en'})
        self.assertEqual(response.status_code, 200)
        return head_links(response.content.decode())

    def test_each_language_version_is_its_own_canonical(self):
        for page, path in self.pages().items():
            with self.subTest(page=page):
                self.assertEqual(self.links_for(path, 'en')[('canonical', None)], HOST + path)
                self.assertEqual(self.links_for(path, 'es')[('canonical', None)], HOST + '/es' + path)

    def test_both_versions_list_the_same_alternates(self):
        for page, path in self.pages().items():
            for language in ('en', 'es'):
                with self.subTest(page=page, language=language):
                    links = self.links_for(path, language)
                    self.assertEqual(links[('alternate', 'en')], HOST + path)
                    self.assertEqual(links[('alternate', 'es')], HOST + '/es' + path)
                    self.assertEqual(links[('alternate', 'x-default')], HOST + path)

    def test_og_url_matches_canonical(self):
        html = self.client.get('/es/posts/?utm_source=linkedin').content.decode()
        self.assertIn(f'<meta property="og:url" content="{HOST}/es/posts/">', html)

    def test_tracking_parameters_do_not_reach_the_canonical(self):
        links = head_links(self.client.get('/posts/?utm_source=linkedin').content.decode())
        self.assertEqual(links[('canonical', None)], HOST + '/posts/')

    def test_category_filter_keeps_its_own_canonical_and_alternates(self):
        links = head_links(self.client.get('/es/posts/?category=idea').content.decode())
        self.assertEqual(links[('canonical', None)], HOST + '/es/posts/?category=idea')
        self.assertEqual(links[('alternate', 'en')], HOST + '/posts/?category=idea')

    def test_private_pages_get_no_alternates(self):
        html = self.client.get(reverse('portfolio:login')).content.decode()
        self.assertNotIn('hreflang', html)


class SitemapTest(BasePublicPagesTest):

    def sitemap(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        return response.content.decode()

    def locations(self):
        return re.findall(r'<loc>([^<]*)</loc>', self.sitemap())

    def test_lists_both_languages_of_every_page(self):
        locations = self.locations()
        for path in ('/', '/posts/', '/resume/',
                     f'/post/{self.post.slug}/', f'/project/{self.project.slug}/'):
            with self.subTest(path=path):
                self.assertIn(HOST + path, locations)
                self.assertIn(HOST + '/es' + path, locations)

    def test_entries_declare_their_alternates(self):
        xml = self.sitemap()
        self.assertIn(f'hreflang="es" href="{HOST}/es/posts/"', xml)
        self.assertIn(f'hreflang="x-default" href="{HOST}/posts/"', xml)

    def test_categories_without_published_posts_are_left_out(self):
        empty = Category.objects.create(slug='empty')
        empty.set_current_language('en')
        empty.name = "Empty"
        empty.save()

        drafts = Category.objects.create(slug='drafts-only')
        drafts.set_current_language('en')
        drafts.name = "Drafts only"
        drafts.save()
        draft = BlogPost()
        draft.set_current_language('en')
        draft.title = "Draft"
        draft.content = "Body"
        draft.category = drafts
        draft.status = 'draft'
        draft.publish_date = timezone.now()
        draft.save()

        xml = self.sitemap()
        self.assertIn('category=idea', xml)
        self.assertNotIn('category=empty', xml)
        self.assertNotIn('category=drafts-only', xml)

    def test_a_category_is_listed_once_per_language(self):
        second = BlogPost()
        second.set_current_language('en')
        second.title = "Second post"
        second.content = "Body"
        second.category = self.category
        second.status = 'published'
        second.publish_date = timezone.now()
        second.save()

        self.assertEqual(self.locations().count(HOST + '/posts/?category=idea'), 1)
        self.assertEqual(self.locations().count(HOST + '/es/posts/?category=idea'), 1)


class DescriptionTruncationTest(SimpleTestCase):

    def test_short_text_is_untouched(self):
        self.assertEqual(SEOGenerator._truncate("A short bio."), "A short bio.")

    def test_long_text_is_cut_between_words(self):
        text = "word " * 60
        result = SEOGenerator._truncate(text)
        self.assertLessEqual(len(result), 160)
        self.assertTrue(result.endswith("word…"))

    def test_no_dangling_punctuation_before_the_ellipsis(self):
        text = "x" * 150 + ", " + "y" * 40
        self.assertEqual(SEOGenerator._truncate(text), "x" * 150 + "…")

    def test_a_single_very_long_word_is_still_cut(self):
        self.assertEqual(len(SEOGenerator._truncate("x" * 400)), 160)

    def test_home_description_uses_it(self):
        from types import SimpleNamespace
        bio = "Engineer building things. " * 20
        profile = SimpleNamespace(name="Ada", title="Engineer", bio=bio, profile_image=None)
        with translation.override('en'):
            description = SEOGenerator.generate_home_seo(profile)['description']
        self.assertLessEqual(len(description), 160)
        self.assertTrue(description.endswith("…"))


class ResumeWordingTest(SimpleTestCase):

    def test_spanish_calls_the_resume_a_cv(self):
        """It was "Resumen", which means "summary"."""
        with translation.override('es'):
            self.assertEqual(translation.gettext("Resume"), "CV")
