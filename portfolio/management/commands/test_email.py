"""
Management command to test email configuration.
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from portfolio.models import Profile
from portfolio.email_service import EmailService


class Command(BaseCommand):
    help = 'Test email configuration by sending a test email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            help='Email address to send test email to (defaults to profile email)',
        )
        parser.add_argument(
            '--service',
            action='store_true',
            help='Use EmailService test method instead of direct send_mail',
        )

    def handle(self, *args, **options):
        self.stdout.write('Testing email configuration...\n')

        # Get recipient email
        recipient_email = options.get('to')
        if not recipient_email:
            try:
                profile = Profile.objects.first()
                if profile and profile.email:
                    recipient_email = profile.email
                else:
                    self.stdout.write(
                        self.style.ERROR('No profile email found. Please specify --to email@example.com')
                    )
                    return
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error getting profile: {e}')
                )
                return

        self.stdout.write(f'Recipient: {recipient_email}')
        self.stdout.write(f'From email: {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write(f'Email backend: {settings.EMAIL_BACKEND}')

        if hasattr(settings, 'EMAIL_HOST'):
            self.stdout.write(f'Email host: {settings.EMAIL_HOST}')
            self.stdout.write(f'Email port: {settings.EMAIL_PORT}')
            self.stdout.write(f'Use TLS: {getattr(settings, "EMAIL_USE_TLS", False)}')

        self.stdout.write('\nSending test email...')

        try:
            if options.get('service'):
                # Use EmailService test method
                result = EmailService.test_email_configuration()
                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ {result["message"]}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ {result["message"]}')
                    )
            else:
                # Direct send_mail test
                subject = 'Test Email - Portfolio Management Command'
                message = '''
This is a test email sent from the Django management command.

If you received this email, your email configuration is working correctly!

Email settings:
- Backend: {backend}
- From: {from_email}
- Host: {host}

Best regards,
Your Portfolio System
                '''.format(
                    backend=settings.EMAIL_BACKEND,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    host=getattr(settings, 'EMAIL_HOST', 'Not configured')
                )

                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )

                self.stdout.write(
                    self.style.SUCCESS(f'✅ Test email sent successfully to {recipient_email}')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to send test email: {e}')
            )
            
            # Provide helpful troubleshooting info
            self.stdout.write('\n🔧 Troubleshooting tips:')
            self.stdout.write('1. Check your .env file has correct EMAIL_* settings')
            self.stdout.write('2. For Gmail, use an App Password instead of your regular password')
            self.stdout.write('3. Verify EMAIL_HOST and EMAIL_PORT are correct for your provider')
            self.stdout.write('4. Check if EMAIL_USE_TLS or EMAIL_USE_SSL is needed')
            self.stdout.write('5. Ensure DEFAULT_FROM_EMAIL is a valid email address')

        self.stdout.write('\nEmail configuration test completed.')