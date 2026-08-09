"""Tests for the CSP analytics origin (issue #117)."""
from django.core.cache import cache
from django.http import HttpResponse
from django.test import TestCase, RequestFactory

from portfolio.middleware.security import SecurityHeadersMiddleware, get_analytics_origin
from portfolio.models import SiteConfiguration


class CspAnalyticsOriginTest(TestCase):

    def setUp(self):
        cache.delete('umami_analytics_origin')
        self.factory = RequestFactory()
        self.middleware = SecurityHeadersMiddleware(lambda request: HttpResponse())

    def _csp(self):
        request = self.factory.get('/')
        response = self.middleware.process_response(request, HttpResponse())
        return response['Content-Security-Policy']

    def test_no_analytics_origin_without_configuration(self):
        csp = self._csp()
        self.assertNotIn('analytics.henfrydls.com', csp)
        self.assertNotIn('stats.example.com', csp)

    def test_configured_origin_in_script_and_connect_src(self):
        config = SiteConfiguration.get_solo()
        config.umami_script_url = 'https://stats.example.com/script.js'
        config.save()
        cache.delete('umami_analytics_origin')
        csp = self._csp()
        directives = {d.strip().split(' ')[0]: d.strip() for d in csp.split(';') if d.strip()}
        self.assertIn('https://stats.example.com', directives['script-src'])
        self.assertIn('https://stats.example.com', directives['connect-src'])
        self.assertNotIn('analytics.henfrydls.com', csp)

    def test_helper_returns_origin_only(self):
        config = SiteConfiguration.get_solo()
        config.umami_script_url = 'https://stats.example.com/script.js'
        config.save()
        cache.delete('umami_analytics_origin')
        self.assertEqual(get_analytics_origin(), 'https://stats.example.com')

    def test_cache_invalidated_on_configuration_save(self):
        config = SiteConfiguration.get_solo()
        config.umami_script_url = 'https://stats.example.com/script.js'
        config.save()
        self.assertEqual(get_analytics_origin(), 'https://stats.example.com')

        config.umami_script_url = 'https://updated.example.com/script.js'
        config.save()

        self.assertEqual(get_analytics_origin(), 'https://updated.example.com')
