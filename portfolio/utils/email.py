"""
Email service for portfolio application.
Handles sending contact notifications and confirmations.
"""
import logging
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

logger = logging.getLogger('portfolio')


class EmailService:
    """Service class for handling email operations."""
    
    @staticmethod
    def send_contact_notification(contact, request_meta=None):
        """
        Send email notification to site owner when contact form is submitted.
        
        Args:
            contact: Contact model instance
            request_meta: Request META data for IP and user agent
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        from ..models import Profile
        try:
            profile = Profile.objects.first()
            if not profile or not profile.email:
                logger.warning('No profile email configured for contact notifications')
                return False
            
            # Prepare context for email templates
            context = {
                'contact': contact,
                'profile': profile,
                'ip_address': EmailService._get_client_ip(request_meta) if request_meta else 'Unknown',
                'user_agent': request_meta.get('HTTP_USER_AGENT', 'Unknown') if request_meta else 'Unknown',
            }
            
            # Render email templates
            html_content = render_to_string('portfolio/email/contact_notification.html', context)
            text_content = render_to_string('portfolio/email/contact_notification.txt', context)
            
            # Create email
            subject = f"Nuevo mensaje de contacto: {contact.subject}"
            
            # Send email
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[profile.email],
                reply_to=[contact.email]  # Allow direct reply to sender
            )
            msg.attach_alternative(html_content, "text/html")
            
            msg.send()
            
            logger.info(f'Contact notification email sent to {profile.email} for message from {contact.email}')
            return True
            
        except Exception as e:
            logger.error(f'Failed to send contact notification email: {e}')
            return False
    
    @staticmethod
    def send_contact_confirmation(contact):
        """
        Send confirmation email to user who submitted contact form.
        
        Args:
            contact: Contact model instance
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        from ..models import Profile
        try:
            profile = Profile.objects.first()
            if not profile:
                logger.warning('No profile configured for contact confirmation')
                return False
            
            # Check if confirmation emails are enabled (could be a setting)
            if not getattr(settings, 'SEND_CONTACT_CONFIRMATIONS', True):
                logger.info('Contact confirmations disabled in settings')
                return True
            
            # Prepare context for email templates
            context = {
                'contact': contact,
                'profile': profile,
            }
            
            # Render email templates
            html_content = render_to_string('portfolio/email/contact_confirmation.html', context)
            text_content = render_to_string('portfolio/email/contact_confirmation.txt', context)
            
            # Create email
            subject = f"Confirmación: Tu mensaje ha sido recibido - {contact.subject}"
            
            # Send email
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[contact.email],
                reply_to=[profile.email] if profile.email else None
            )
            msg.attach_alternative(html_content, "text/html")
            
            msg.send()
            
            logger.info(f'Contact confirmation email sent to {contact.email}')
            return True
            
        except Exception as e:
            logger.error(f'Failed to send contact confirmation email to {contact.email}: {e}')
            
            # Log additional info for external domains
            domain = contact.email.split('@')[1] if '@' in contact.email else 'unknown'
            if domain.lower() not in ['gmail.com', 'googlemail.com']:
                logger.warning(f'Email sent to external domain ({domain}). Delivery may be delayed or blocked by recipient server.')
            
            return False
    
    @staticmethod
    def test_email_configuration():
        """
        Test email configuration by sending a test email.
        
        Returns:
            dict: Test results with success status and message
        """
        from ..models import Profile
        try:
            profile = Profile.objects.first()
            if not profile or not profile.email:
                return {
                    'success': False,
                    'message': 'No profile email configured. Please set up your profile email in the admin panel.'
                }
            
            # Send test email
            subject = 'Test Email - Portfolio Configuration'
            message = '''
This is a test email to verify your portfolio email configuration is working correctly.

If you received this email, your email settings are properly configured!

Best regards,
Your Portfolio System
            '''
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[profile.email],
                fail_silently=False,
            )
            
            logger.info(f'Test email sent successfully to {profile.email}')
            return {
                'success': True,
                'message': f'Test email sent successfully to {profile.email}'
            }
            
        except Exception as e:
            logger.error(f'Email configuration test failed: {e}')
            return {
                'success': False,
                'message': f'Email test failed: {str(e)}'
            }
    
    @staticmethod
    def _get_client_ip(request_meta):
        """Extract client IP from request META."""
        if not request_meta:
            return 'Unknown'
            
        x_forwarded_for = request_meta.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request_meta.get('REMOTE_ADDR', 'Unknown')
        return ip


class EmailConfigurationError(Exception):
    """Custom exception for email configuration errors."""
    pass


class EmailDomainChecker:
    """Helper class for checking email domain compatibility."""
    
    @staticmethod
    def check_domain_compatibility(email):
        """
        Check if email domain is likely to receive emails from Gmail.
        
        Args:
            email: Email address to check
            
        Returns:
            dict: Compatibility info with recommendations
        """
        if not email or '@' not in email:
            return {'compatible': False, 'reason': 'Invalid email format'}
        
        domain = email.split('@')[1].lower()
        
        # High compatibility domains
        high_compat = ['gmail.com', 'googlemail.com', 'google.com']
        
        # Medium compatibility domains  
        medium_compat = ['outlook.com', 'hotmail.com', 'live.com', 'msn.com', 
                        'yahoo.com', 'ymail.com', 'aol.com', 'icloud.com']
        
        # Known problematic patterns
        problematic = ['example.com', 'test.com', 'localhost']
        
        if domain in high_compat:
            return {
                'compatible': True,
                'level': 'high',
                'delivery_time': '< 1 minute',
                'recommendation': 'Emails should deliver immediately'
            }
        elif domain in medium_compat:
            return {
                'compatible': True,
                'level': 'medium', 
                'delivery_time': '1-10 minutes',
                'recommendation': 'Emails may take a few minutes to deliver'
            }
        elif domain in problematic:
            return {
                'compatible': False,
                'level': 'none',
                'delivery_time': 'Never',
                'recommendation': 'This is a test/invalid domain'
            }
        else:
            return {
                'compatible': True,
                'level': 'low',
                'delivery_time': '5-30 minutes',
                'recommendation': 'External domain - delivery may be delayed or blocked'
            }