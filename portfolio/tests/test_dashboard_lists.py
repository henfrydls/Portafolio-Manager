"""
Tests for the dashboard list pages.

Searching posts or projects filtered on `title`, `content` and `description`
directly. Those are translated fields, which only exist on the translations
table, so any search raised FieldError and the page answered 500.
"""
from django.urls import reverse

from portfolio.models import BlogPost, Project
from portfolio.tests.test_i18n_language import BasePublicPagesTest, User


class DashboardSearchTest(BasePublicPagesTest):

    def setUp(self):
        super().setUp()
        self.client.force_login(User.objects.get(username='admin'))

        self.post.set_current_language('es')
        self.post.title = "Publicación de prueba"
        self.post.content = "Cuerpo"
        self.post.excerpt = "Resumen"
        self.post.save()

        self.project.set_current_language('es')
        self.project.title = "Proyecto de prueba"
        self.project.description = "Descripción detallada"
        self.project.save()

    def found(self, url_name, search, context_name):
        response = self.client.get(reverse(url_name), {'search': search})
        self.assertEqual(response.status_code, 200)
        return list(response.context[context_name])

    def test_post_search_by_title(self):
        self.assertEqual(self.found('portfolio:admin-blog-list', 'Test Post', 'posts'), [self.post])

    def test_post_search_by_content_and_excerpt(self):
        self.assertEqual(self.found('portfolio:admin-blog-list', 'Post body', 'posts'), [self.post])
        self.assertEqual(self.found('portfolio:admin-blog-list', 'Post excerpt', 'posts'), [self.post])

    def test_post_search_reaches_the_other_language(self):
        self.assertEqual(self.found('portfolio:admin-blog-list', 'Publicación', 'posts'), [self.post])

    def test_post_matching_in_both_languages_is_listed_once(self):
        # "prueba"/"Test" differ, but "p" is in both titles
        self.assertEqual(self.found('portfolio:admin-blog-list', 'p', 'posts'), [self.post])

    def test_post_search_without_matches(self):
        self.assertEqual(self.found('portfolio:admin-blog-list', 'zzz-nothing', 'posts'), [])

    def test_project_search_by_title_and_description(self):
        self.assertEqual(self.found('portfolio:admin-project-list', 'Test Project', 'projects'), [self.project])
        self.assertEqual(
            self.found('portfolio:admin-project-list', 'Detailed project', 'projects'), [self.project])

    def test_project_search_reaches_the_other_language(self):
        self.assertEqual(self.found('portfolio:admin-project-list', 'Proyecto de', 'projects'), [self.project])

    def test_project_matching_in_both_languages_is_listed_once(self):
        self.assertEqual(self.found('portfolio:admin-project-list', 'pro', 'projects'), [self.project])

    def test_project_search_without_matches(self):
        self.assertEqual(self.found('portfolio:admin-project-list', 'zzz-nothing', 'projects'), [])
