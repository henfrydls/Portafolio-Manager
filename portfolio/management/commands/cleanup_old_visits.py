"""
Management command to clean up old page visit data.
This command removes PageVisit records older than 6 months to keep the database optimized.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from portfolio.models import PageVisit


class Command(BaseCommand):
    help = 'Clean up old page visit data (older than 6 months)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=180,
            help='Number of days to keep (default: 180 days / 6 months)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        days_to_keep = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        # Find old records
        old_visits = PageVisit.objects.filter(timestamp__lt=cutoff_date)
        count = old_visits.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'No page visit records older than {days_to_keep} days found.'
                )
            )
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would delete {count} page visit records older than {cutoff_date.date()}'
                )
            )
            
            # Show some examples
            sample_visits = old_visits[:5]
            if sample_visits:
                self.stdout.write('\nSample records that would be deleted:')
                for visit in sample_visits:
                    self.stdout.write(
                        f'  - {visit.timestamp.date()} | {visit.page_url} | {visit.ip_address}'
                    )
                if count > 5:
                    self.stdout.write(f'  ... and {count - 5} more records')
        else:
            # Actually delete the records
            deleted_count, _ = old_visits.delete()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {deleted_count} page visit records older than {cutoff_date.date()}'
                )
            )
            
            # Show remaining count
            remaining_count = PageVisit.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Remaining page visit records: {remaining_count}'
                )
            )