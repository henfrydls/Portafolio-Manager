"""
Management command to set up database cache table.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Create database cache table for production'

    def handle(self, *args, **options):
        self.stdout.write('Creating cache table...')
        try:
            call_command('createcachetable')
            self.stdout.write(
                self.style.SUCCESS('Successfully created cache table')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating cache table: {e}')
            )