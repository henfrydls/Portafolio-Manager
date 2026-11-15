"""
Tests for what the public blog lists (issue #175).

- A published post dated in the future was live immediately.
- A search matching both translations listed the post twice.
- The tag filter matched substrings ("ai" brought "email").
"""
from datetime import timedelta

from django.utils import timezone

from portfolio.models import BlogPost
from portfolio.query_optimizations import QueryOptimizer
from portfolio.tests.test_i18n_language import BasePublicPagesTest


class PublicBlogTestCase(BasePublicPagesTest):

    def make_post(self, slug, title, *, days=-1, tags='', status='published',
                  spanish_title=None, featured=False):
        post = BlogPost()
        post.set_current_language('en')
        post.title = title
        post.content = f"{title} body"
        post.excerpt = f"{title} excerpt"
        post.slug = slug
        post.category = self.category
        post.status = status
        post.tags = tags
        post.featured = featured
        post.publish_date = timezone.now() + timedelta(days=days)
        post.save()
        if spanish_title:
            post.set_current_language('es')
            post.title = spanish_title
            post.content = f"{spanish_title} cuerpo"
            post.excerpt = f"{spanish_title} extracto"
            post.save()
        return post

    def listed(self, query=''):
        response = self.client.get(f'/posts/{query}')
        self.assertEqual(response.status_code, 200)
        return [post.slug for post in response.context['posts']]


class ScheduledPostTest(PublicBlogTestCase):

    def setUp(self):
        super().setUp()
        self.scheduled = self.make_post(
            'next-week', "Next week", days=7, tags='future-tag', featured=True)

    def test_not_in_the_post_list(self):
        self.assertNotIn('next-week', self.listed())

    def test_its_page_does_not_exist_yet(self):
        self.assertEqual(self.client.get('/post/next-week/').status_code, 404)
        self.assertEqual(self.client.get('/es/post/next-week/').status_code, 404)

    def test_not_on_the_home_page(self):
        self.assertNotContains(self.client.get('/'), "Next week")

    def test_not_in_the_optimized_querysets(self):
        self.assertNotIn(self.scheduled, QueryOptimizer.get_optimized_blog_posts())
        self.assertNotIn(
            self.scheduled, QueryOptimizer.get_optimized_blog_posts(featured_only=True))
        # The dashboard asks for every status and still sees it
        self.assertIn(self.scheduled, QueryOptimizer.get_optimized_blog_posts(status='all'))

    def test_its_tags_are_not_offered(self):
        response = self.client.get('/posts/')
        self.assertNotIn('future-tag', response.context['available_tags'])

    def test_not_in_the_sitemap(self):
        self.assertNotContains(self.client.get('/sitemap.xml'), 'next-week')

    def test_goes_live_when_its_date_arrives(self):
        BlogPost.objects.filter(pk=self.scheduled.pk).update(
            publish_date=timezone.now() - timedelta(minutes=1))
        self.assertIn('next-week', self.listed())
        self.assertEqual(self.client.get('/post/next-week/').status_code, 200)
        self.assertContains(self.client.get('/sitemap.xml'), 'next-week')

    def test_drafts_stay_hidden_whatever_their_date(self):
        self.make_post('old-draft', "Old draft", days=-30, status='draft')
        self.assertNotIn('old-draft', self.listed())
        self.assertEqual(self.client.get('/post/old-draft/').status_code, 404)


class BlogSearchTest(PublicBlogTestCase):

    def test_a_post_matching_in_both_languages_is_listed_once(self):
        self.make_post('grid-notes', "Grid notes", spanish_title="Grid en español")
        self.assertEqual(self.listed('?search=grid'), ['grid-notes'])

    def test_search_reaches_the_other_language(self):
        self.make_post('storage', "Storage", spanish_title="Almacenamiento")
        self.assertEqual(self.listed('?search=almacenamiento'), ['storage'])


class TagFilterTest(PublicBlogTestCase):

    def setUp(self):
        super().setUp()
        self.make_post('about-ai', "About AI", tags='ai, energy')
        self.make_post('about-email', "About email", tags='email,maintain')
        self.make_post('ai-last', "AI last", tags='python, AI')

    def test_matches_the_whole_tag_only(self):
        self.assertCountEqual(self.listed('?tag=ai'), ['about-ai', 'ai-last'])

    def test_is_case_insensitive(self):
        self.assertCountEqual(self.listed('?tag=AI'), ['about-ai', 'ai-last'])

    def test_single_tag_and_surrounding_spaces(self):
        self.make_post('only-tag', "Only tag", tags=' solo ')
        self.assertEqual(self.listed('?tag=solo'), ['only-tag'])

    def test_characters_special_to_regular_expressions_are_literal(self):
        self.make_post('cpp', "C plus plus", tags='c++, .net')
        self.assertEqual(self.listed('?tag=c%2B%2B'), ['cpp'])
        self.assertEqual(self.listed('?tag=.net'), ['cpp'])
        self.assertEqual(self.listed('?tag=.*'), [])


class SitemapLastmodTest(PublicBlogTestCase):

    def test_static_pages_use_the_latest_post_not_the_current_time(self):
        latest = BlogPost.objects.order_by('-updated_at').first().updated_at
        response = self.client.get('/sitemap.xml')
        self.assertContains(response, f'<lastmod>{latest.date().isoformat()}</lastmod>')
        home = response.content.decode().split('</url>')[0]
        self.assertIn('<lastmod>', home)
