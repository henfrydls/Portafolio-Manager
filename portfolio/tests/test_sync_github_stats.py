"""
Tests for the sync_github_stats management command.

Every GitHub call is mocked; these tests never touch the network.
"""
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from portfolio.management.commands.sync_github_stats import Command
from portfolio.models import Project


def make_project(title, **fields):
    project = Project()
    project.set_current_language('en')
    project.title = title
    project.description = f'{title} description'
    for field, value in fields.items():
        setattr(project, field, value)
    project.save()
    return project


class FakeResponse:
    """Minimal stand-in for requests.Response."""

    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.content = b'{}'

    def json(self):
        return self._payload


def repo_payload(stars=0, forks=0, language='Python', owner='henfrydls'):
    return {
        'stargazers_count': stars,
        'forks_count': forks,
        'language': language,
        'owner': {'login': owner},
    }


class ParseRepoTest(TestCase):
    """The URL parser is what decides which repo gets queried."""

    def test_parses_plain_repo_url(self):
        self.assertEqual(
            Command._parse_repo('https://github.com/henfrydls/Skima'),
            ('henfrydls', 'Skima')
        )

    def test_tolerates_trailing_slash_git_suffix_and_www(self):
        for url in (
            'https://github.com/henfrydls/daylo/',
            'https://github.com/henfrydls/daylo.git',
            'https://www.github.com/henfrydls/daylo',
        ):
            with self.subTest(url=url):
                self.assertEqual(Command._parse_repo(url), ('henfrydls', 'daylo'))

    def test_parses_deep_link(self):
        self.assertEqual(
            Command._parse_repo('https://github.com/henfrydls/daylo/tree/main'),
            ('henfrydls', 'daylo')
        )

    def test_rejects_non_repo_urls(self):
        for url in (
            'https://github.com/henfrydls',
            'https://github.com/',
            'https://gitlab.com/henfrydls/daylo',
            '',
        ):
            with self.subTest(url=url):
                self.assertIsNone(Command._parse_repo(url))


class SyncGithubStatsCommandTest(TestCase):

    def run_command(self, payload=None, status_code=200, **options):
        response = FakeResponse(payload or repo_payload(), status_code)
        with patch('requests.Session.get', return_value=response) as mocked:
            out = StringIO()
            call_command('sync_github_stats', stdout=out, **options)
        return out.getvalue(), mocked

    def test_updates_stars_and_forks(self):
        project = make_project('Skima', github_url='https://github.com/henfrydls/Skima')

        self.run_command(repo_payload(stars=3, forks=1))

        project.refresh_from_db()
        self.assertEqual(project.stars_count, 3)
        self.assertEqual(project.forks_count, 1)

    def test_dry_run_leaves_database_untouched(self):
        project = make_project(
            'Skima', github_url='https://github.com/henfrydls/Skima', stars_count=0
        )

        output, _ = self.run_command(repo_payload(stars=3), dry_run=True)

        project.refresh_from_db()
        self.assertEqual(project.stars_count, 0)
        self.assertIn('DRY RUN', output)

    def test_skips_private_projects(self):
        make_project(
            'Internal tool',
            github_url='https://github.com/henfrydls/internal',
            is_private_project=True,
            stars_count=7,
        )

        output, mocked = self.run_command(repo_payload(stars=99))

        mocked.assert_not_called()
        self.assertIn('No public projects', output)

    def test_does_not_overwrite_an_existing_primary_language(self):
        project = make_project(
            'Portfolio Manager',
            github_url='https://github.com/henfrydls/Portafolio-Manager',
            primary_language='python',
        )

        self.run_command(repo_payload(language='Python'))

        project.refresh_from_db()
        self.assertEqual(project.primary_language, 'python')

    def test_fills_blank_owner_and_language(self):
        project = make_project(
            'Daylo', github_url='https://github.com/henfrydls/daylo'
        )

        self.run_command(repo_payload(language='TypeScript', owner='henfrydls'))

        project.refresh_from_db()
        self.assertEqual(project.github_owner, 'henfrydls')
        self.assertEqual(project.primary_language, 'TypeScript')

    def test_reports_failure_without_touching_counters(self):
        project = make_project(
            'Gone', github_url='https://github.com/henfrydls/gone', stars_count=5
        )

        output, _ = self.run_command({'message': 'Not Found'}, status_code=404)

        project.refresh_from_db()
        self.assertEqual(project.stars_count, 5)
        self.assertIn('1 failed', output)

    def test_unparseable_url_is_reported_and_not_requested(self):
        make_project('Broken', github_url='https://example.com/not-a-repo')

        output, mocked = self.run_command()

        mocked.assert_not_called()
        self.assertIn('1 failed', output)

    def test_second_run_reports_nothing_to_change(self):
        make_project(
            'Skima',
            github_url='https://github.com/henfrydls/Skima',
            github_owner='henfrydls',
            primary_language='JavaScript',
        )
        payload = repo_payload(stars=3, forks=1, language='JavaScript')

        self.run_command(payload)
        output, _ = self.run_command(payload)

        self.assertIn('0 updated, 1 already current, 0 failed', output)
