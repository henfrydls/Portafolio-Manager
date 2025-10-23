"""
Management command to clean up page visits from admin/dashboard/analytics pages.
These visits should not have been recorded and need to be removed from analytics.
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from portfolio.models import PageVisit


class Command(BaseCommand):
    help = 'Remove page visits from admin, dashboard, analytics, and setup pages'

    # Same excluded paths as in PageVisitMiddleware
    EXCLUDED_PATHS = [
        '/admin/',
        '/static/',
        '/media/',
        '/favicon.ico',
        '/robots.txt',
        '/sitemap.xml',
        '/.well-known/',
        '/apple-touch-icon',
        '/browserconfig.xml',
        '/manifest.json',
        '/api/',
        '/manage/ajax/',
        '/setup/',
        '/dashboard/',
        '/analytics/',
        '/admin-dashboard/',
        '/admin-analytics/',
        '/login/',
        '/logout/',
        '/password-change/',
        '/manage/',
    ]

    EXCLUDED_PATTERNS = [
        '.well-known',
        'devtools',
        'chrome-extension',
        'moz-extension',
        'safari-extension',
        'edge-extension',
        '__webpack',
        'hot-update',
        '.map',
        'sourcemap',
    ]

    BOT_USER_AGENTS = [
        'googlebot',
        'bingbot',
        'slurp',
        'duckduckbot',
        'baiduspider',
        'yandexbot',
        'facebookexternalhit',
        'linkedinbot',
        'whatsapp',
        'telegram',
        'bot',
        'crawler',
        'spider',
        'scraper',
        'curl',
        'wget',
        'python-requests',
        'postman',
        'insomnia',
        'httpie',
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
        parser.add_argument(
            '--show-sample',
            action='store_true',
            help='Show sample records that will be deleted'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        show_sample = options['show_sample']

        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("Cleanup Admin Page Visits"))
        self.stdout.write("="*60 + "\n")

        # Build query for invalid visits
        invalid_conditions = Q()

        # Add conditions for excluded paths
        for excluded_path in self.EXCLUDED_PATHS:
            invalid_conditions |= Q(page_url__startswith=excluded_path)

        # Add conditions for excluded patterns
        for pattern in self.EXCLUDED_PATTERNS:
            invalid_conditions |= Q(page_url__icontains=pattern)

        # Add conditions for bot user agents
        for bot in self.BOT_USER_AGENTS:
            invalid_conditions |= Q(user_agent__icontains=bot)

        # Get invalid visits
        invalid_visits = PageVisit.objects.filter(invalid_conditions)
        count = invalid_visits.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    '✅ No admin/dashboard/analytics visits found. Database is clean!'
                )
            )
            return

        # Show statistics
        self.stdout.write(f"Found {count} invalid page visits to clean up:\n")

        # Count by category
        admin_count = PageVisit.objects.filter(page_url__startswith='/admin/').count()
        dashboard_count = PageVisit.objects.filter(page_url__startswith='/dashboard/').count()
        analytics_count = PageVisit.objects.filter(page_url__startswith='/analytics/').count()
        setup_count = PageVisit.objects.filter(page_url__startswith='/setup/').count()
        manage_count = PageVisit.objects.filter(page_url__startswith='/manage/').count()
        bot_count = 0
        for bot in self.BOT_USER_AGENTS:
            bot_count += PageVisit.objects.filter(user_agent__icontains=bot).count()

        if admin_count > 0:
            self.stdout.write(f"  - Admin pages: {admin_count}")
        if dashboard_count > 0:
            self.stdout.write(f"  - Dashboard pages: {dashboard_count}")
        if analytics_count > 0:
            self.stdout.write(f"  - Analytics pages: {analytics_count}")
        if setup_count > 0:
            self.stdout.write(f"  - Setup pages: {setup_count}")
        if manage_count > 0:
            self.stdout.write(f"  - Management pages: {manage_count}")
        if bot_count > 0:
            self.stdout.write(f"  - Bot visits: {bot_count}")

        # Show sample if requested
        if show_sample or dry_run:
            self.stdout.write("\nSample records to be deleted:")
            sample_visits = invalid_visits[:10]
            for visit in sample_visits:
                user_agent_preview = visit.user_agent[:50] + '...' if len(visit.user_agent) > 50 else visit.user_agent
                self.stdout.write(
                    f"  - {visit.timestamp.strftime('%Y-%m-%d %H:%M')} | {visit.page_url} | {visit.ip_address}"
                )
                self.stdout.write(f"    UA: {user_agent_preview}")
            if count > 10:
                self.stdout.write(f"  ... and {count - 10} more records\n")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\n⚠️  DRY RUN: Would delete {count} invalid page visits'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    'Run without --dry-run to actually delete these records\n'
                )
            )
        else:
            # Confirm before deleting
            self.stdout.write(
                self.style.WARNING(
                    f'\n⚠️  About to delete {count} page visit records'
                )
            )

            # Actually delete the records
            deleted_count, _ = invalid_visits.delete()

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Successfully deleted {deleted_count} invalid page visits'
                )
            )

            # Show remaining count
            remaining_count = PageVisit.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f'📊 Remaining page visit records: {remaining_count}'
                )
            )

        self.stdout.write("\n" + "="*60 + "\n")
