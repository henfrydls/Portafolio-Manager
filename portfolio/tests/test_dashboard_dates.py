"""
Tests for "today" and "yesterday" in the dashboard (issue #176).

The views took the UTC date and compared it with `timestamp__date`, which
the database evaluates in TIME_ZONE. West of Greenwich the two disagree
every evening: "today" read 0 and "yesterday" showed today's visits.
"""
import json
from datetime import datetime, timezone as dt_timezone
from unittest import mock
from zoneinfo import ZoneInfo

from django.test import override_settings
from django.urls import reverse

from portfolio.models import PageVisit
from portfolio.tests.test_i18n_language import BasePublicPagesTest, User
from portfolio.utils.analytics import get_analytics_summary

LOCAL = ZoneInfo('America/Santo_Domingo')  # UTC-4, no daylight saving

# 21:30 on the 12th locally is already 01:30 on the 13th in UTC
EVENING = datetime(2026, 11, 12, 21, 30, tzinfo=LOCAL).astimezone(dt_timezone.utc)


def visit_at(year, month, day, hour, minute=0):
    visit = PageVisit.objects.create(page_url='/', ip_address='203.0.113.7')
    # auto_now_add ignores a value passed to create()
    PageVisit.objects.filter(pk=visit.pk).update(
        timestamp=datetime(year, month, day, hour, minute, tzinfo=LOCAL))
    return visit


@override_settings(TIME_ZONE='America/Santo_Domingo', USE_TZ=True)
class DashboardLocalDatesTest(BasePublicPagesTest):

    def setUp(self):
        super().setUp()
        self.client.force_login(User.objects.get(username='admin'))
        PageVisit.objects.all().delete()
        visit_at(2026, 11, 12, 10)        # today, morning
        visit_at(2026, 11, 12, 20, 30)    # today, after the UTC date changed
        visit_at(2026, 11, 11, 23)        # yesterday, late
        visit_at(2026, 11, 10, 12)        # two days ago
        patcher = mock.patch('django.utils.timezone.now', return_value=EVENING)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_dashboard_counts_the_local_day(self):
        context = self.client.get(reverse('portfolio:admin-dashboard')).context
        self.assertEqual(context['today_visits'], 2)
        self.assertEqual(context['yesterday_visits'], 1)

    def test_analytics_counts_the_local_day(self):
        stats = self.client.get(reverse('portfolio:admin-analytics')).context['visit_stats']
        self.assertEqual(stats['today_visits'], 2)
        self.assertEqual(stats['yesterday_visits'], 1)

    def test_daily_chart_ends_on_the_local_day(self):
        chart = self.client.get(reverse('portfolio:admin-analytics')).context['daily_visits_chart']
        labels = json.loads(chart['labels'])
        data = json.loads(chart['data'])
        self.assertEqual(labels[-1], '2026-11-12')
        self.assertEqual(data[-3:], [1, 1, 2])

    def test_summary_counts_the_local_day(self):
        self.assertEqual(get_analytics_summary()['today_visits'], 2)
