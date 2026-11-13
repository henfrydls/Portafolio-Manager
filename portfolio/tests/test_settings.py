"""
The suite must exercise the middleware stack that production runs (issue #144).
"""
from django.conf import settings
from django.test import SimpleTestCase

from config.settings import base


class TestSettingsMiddlewareTest(SimpleTestCase):

    def test_tests_run_with_the_production_middleware_stack(self):
        self.assertEqual(list(settings.MIDDLEWARE), list(base.MIDDLEWARE))

    def test_project_middlewares_are_active(self):
        for name in (
            'portfolio.middleware.InitialSetupRedirectMiddleware',
            'portfolio.middleware.SiteLanguageMiddleware',
            'portfolio.middleware.PageVisitMiddleware',
            'portfolio.middleware.security.SecurityHeadersMiddleware',
        ):
            with self.subTest(middleware=name):
                self.assertIn(name, settings.MIDDLEWARE)
