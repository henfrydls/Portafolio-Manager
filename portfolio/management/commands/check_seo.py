"""
Management command to check SEO implementation and generate reports.
"""

from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse
from portfolio.models import Profile, Project, BlogPost
from portfolio.seo_utils import SEOGenerator
import json

class Command(BaseCommand):
    help = 'Check SEO implementation and generate reports'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            choices=['text', 'json'],
            default='text',
            help='Output format',
        )
        
        parser.add_argument(
            '--check-urls',
            action='store_true',
            help='Check if SEO URLs are accessible',
        )
    
    def handle(self, *args, **options):
        output_format = options['format']
        check_urls = options['check_urls']
        
        self.stdout.write(
            self.style.SUCCESS('Checking SEO implementation...')
        )
        
        # Check SEO utilities
        seo_report = self.check_seo_utilities()
        
        # Check URLs if requested
        if check_urls:
            url_report = self.check_seo_urls()
            seo_report['urls'] = url_report
        
        # Output results
        if output_format == 'json':
            self.stdout.write(json.dumps(seo_report, indent=2, default=str))
        else:
            self.print_text_report(seo_report)
    
    def check_seo_utilities(self):
        """Check SEO utilities functionality."""
        report = {
            'seo_generator': True,
            'profile_seo': False,
            'project_seo': False,
            'blog_seo': False,
            'structured_data': False,
            'errors': []
        }
        
        try:
            # Test profile SEO
            profile = Profile.objects.first()
            if profile:
                profile_seo = SEOGenerator.generate_home_seo(profile)
                report['profile_seo'] = bool(profile_seo.get('title'))
                
                # Test structured data
                structured_data = SEOGenerator.generate_structured_data_person(profile)
                report['structured_data'] = bool(structured_data.get('@type'))
            
            # Test project SEO
            project = Project.objects.filter(visibility='public').first()
            if project:
                project_seo = SEOGenerator.generate_project_seo(project)
                report['project_seo'] = bool(project_seo.get('title'))
            
            # Test blog SEO
            blog_post = BlogPost.objects.filter(status='published').first()
            if blog_post:
                blog_seo = SEOGenerator.generate_blog_post_seo(blog_post)
                report['blog_seo'] = bool(blog_seo.get('title'))
                
        except Exception as e:
            report['errors'].append(f'SEO utilities error: {e}')
        
        return report
    
    def check_seo_urls(self):
        """Check SEO-related URLs."""
        client = Client()
        urls_to_check = [
            ('/robots.txt', 'robots.txt'),
            ('/sitemap.xml', 'sitemap.xml'),
            ('/.well-known/security.txt', 'security.txt'),
            ('/manifest.json', 'manifest.json'),
        ]
        
        url_report = {}
        
        for url, name in urls_to_check:
            try:
                response = client.get(url, HTTP_HOST='localhost')
                url_report[name] = {
                    'status_code': response.status_code,
                    'accessible': response.status_code == 200,
                    'content_type': response.get('Content-Type', 'Unknown')
                }
            except Exception as e:
                url_report[name] = {
                    'status_code': None,
                    'accessible': False,
                    'error': str(e)
                }
        
        return url_report
    
    def print_text_report(self, report):
        """Print SEO report in text format."""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('SEO IMPLEMENTATION REPORT')
        self.stdout.write('='*50)
        
        # SEO Utilities
        self.stdout.write('\n📊 SEO Utilities:')
        self.print_status('SEO Generator', report['seo_generator'])
        self.print_status('Profile SEO', report['profile_seo'])
        self.print_status('Project SEO', report['project_seo'])
        self.print_status('Blog SEO', report['blog_seo'])
        self.print_status('Structured Data', report['structured_data'])
        
        # URLs
        if 'urls' in report:
            self.stdout.write('\n🔗 SEO URLs:')
            for name, data in report['urls'].items():
                status = '✅' if data['accessible'] else '❌'
                self.stdout.write(f'  {status} {name}: {data["status_code"]} ({data.get("content_type", "Unknown")})')
        
        # Errors
        if report['errors']:
            self.stdout.write('\n❌ Errors:')
            for error in report['errors']:
                self.stdout.write(f'  - {error}')
        
        # Summary
        total_checks = 5  # SEO utilities checks
        passed_checks = sum([
            report['seo_generator'],
            report['profile_seo'],
            report['project_seo'],
            report['blog_seo'],
            report['structured_data']
        ])
        
        if 'urls' in report:
            url_checks = len(report['urls'])
            url_passed = sum(1 for data in report['urls'].values() if data['accessible'])
            total_checks += url_checks
            passed_checks += url_passed
        
        self.stdout.write(f'\n📈 Summary: {passed_checks}/{total_checks} checks passed')
        
        if passed_checks == total_checks:
            self.stdout.write(
                self.style.SUCCESS('🎉 All SEO checks passed!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  {total_checks - passed_checks} checks failed')
            )
    
    def print_status(self, name, status):
        """Print status with emoji."""
        emoji = '✅' if status else '❌'
        self.stdout.write(f'  {emoji} {name}')