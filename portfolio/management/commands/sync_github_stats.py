"""
Management command to sync stars, forks and primary language from the GitHub API.

The Project model advertises that stars_count/forks_count update automatically,
but nothing ever populated them. This command does, and is meant to run on a cron.

Private projects are skipped on purpose: their counters are manual estimates.
"""

import os
import re
from urllib.parse import urlparse

import requests
from django.core.management.base import BaseCommand

from portfolio.models import Project

GITHUB_API = 'https://api.github.com/repos/{owner}/{repo}'
# Takes the first two path segments, so deep links like /owner/repo/tree/main work too.
REPO_PATH_RE = re.compile(r'^/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?(?:/.*)?$')


class Command(BaseCommand):
    help = 'Sync stars, forks and primary language for public GitHub projects'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would change without writing to the database'
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=10,
            help='Per-request timeout in seconds (default: 10)'
        )
        parser.add_argument(
            '--slug',
            help='Sync a single project by slug instead of all of them'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        timeout = options['timeout']

        projects = Project.objects.exclude(github_url='').filter(is_private_project=False)
        if options['slug']:
            projects = projects.filter(slug=options['slug'])
        projects = projects.order_by('id')

        if not projects.exists():
            self.stdout.write(self.style.WARNING('No public projects with a GitHub URL found.'))
            return

        session = requests.Session()
        session.headers.update({
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
            'User-Agent': 'henfrydls-portfolio-sync',
        })
        token = os.environ.get('GITHUB_TOKEN', '').strip()
        if token:
            session.headers['Authorization'] = f'Bearer {token}'

        updated = unchanged = failed = 0

        for project in projects:
            name = str(project)
            repo_id = self._parse_repo(project.github_url)
            if not repo_id:
                self.stdout.write(self.style.WARNING(
                    f'  ! {name}: cannot parse a repo out of {project.github_url}'
                ))
                failed += 1
                continue

            owner, repo = repo_id
            try:
                response = session.get(
                    GITHUB_API.format(owner=owner, repo=repo), timeout=timeout
                )
            except requests.RequestException as exc:
                self.stdout.write(self.style.ERROR(f'  ! {name}: request failed ({exc})'))
                failed += 1
                continue

            if response.status_code != 200:
                detail = response.json().get('message', '') if response.content else ''
                self.stdout.write(self.style.ERROR(
                    f'  ! {name}: GitHub returned {response.status_code} {detail}'.rstrip()
                ))
                failed += 1
                continue

            data = response.json()
            changes = {}

            stars = data.get('stargazers_count', 0)
            if stars != project.stars_count:
                changes['stars_count'] = stars

            forks = data.get('forks_count', 0)
            if forks != project.forks_count:
                changes['forks_count'] = forks

            # Only fill these in when empty; a human may have set them deliberately.
            if not project.github_owner:
                changes['github_owner'] = data.get('owner', {}).get('login', owner)
            if not project.primary_language and data.get('language'):
                changes['primary_language'] = data['language']

            if not changes:
                unchanged += 1
                self.stdout.write(f'  = {name}: {stars} stars, {forks} forks')
                continue

            summary = ', '.join(
                f'{field} {getattr(project, field)!r} -> {value!r}'
                for field, value in changes.items()
            )
            if dry_run:
                self.stdout.write(self.style.WARNING(f'  ~ {name}: would set {summary}'))
            else:
                # .update() on purpose: Project.save() re-optimizes the image file on
                # every call, so a scheduled save() would slowly degrade it.
                Project.objects.filter(pk=project.pk).update(**changes)
                self.stdout.write(self.style.SUCCESS(f'  * {name}: {summary}'))
            updated += 1

        prefix = 'DRY RUN: ' if dry_run else ''
        line = f'{prefix}{updated} updated, {unchanged} already current, {failed} failed'
        style = self.style.ERROR if failed else self.style.SUCCESS
        self.stdout.write(style(line))

    @staticmethod
    def _parse_repo(url):
        """Return (owner, repo) for a github.com URL, or None."""
        parsed = urlparse(url)
        if parsed.netloc.lower() not in ('github.com', 'www.github.com'):
            return None
        match = REPO_PATH_RE.match(parsed.path)
        if not match:
            return None
        return match.group('owner'), match.group('repo')
