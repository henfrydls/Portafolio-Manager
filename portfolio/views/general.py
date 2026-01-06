import logging
import uuid
import os
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext as _
from django.views.generic import TemplateView, View
from django.core.files.storage import default_storage

from ..models import Profile, Contact
from ..forms.contact import SecureContactFormWithHoneypot
from ..utils.email import EmailService
from ..utils.seo import SEOGenerator
from ..query_optimizations import QueryOptimizer

logger = logging.getLogger('portfolio')


class HomeView(TemplateView):
    template_name = 'portfolio/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get optimized profile with all related data
        context['profile'] = QueryOptimizer.get_optimized_profile()

        # Get optimized projects for home page sections
        context['featured_projects'] = QueryOptimizer.get_featured_projects()
        context['recent_projects'] = QueryOptimizer.get_recent_projects(limit=6)

        # Get optimized blog posts
        context['featured_posts'] = QueryOptimizer.get_featured_posts()
        context['latest_posts'] = QueryOptimizer.get_latest_posts(limit=3)

        # Get mixed featured items (projects + posts) for Featured Work section
        context['featured_items'] = QueryOptimizer.get_featured_items_optimized(limit=4)

        # Paginate all public projects for "Work & Projects" section
        all_projects = QueryOptimizer.get_optimized_projects(visibility='public', featured_only=False)
        projects_page = self.request.GET.get('projects_page', 1)
        projects_paginator = Paginator(all_projects, 10)  # 10 projects per page
        projects_page_obj = projects_paginator.get_page(projects_page)

        context['projects'] = projects_page_obj
        context['projects_paginator'] = projects_paginator
        context['projects_page_obj'] = projects_page_obj

        # Add SEO context
        context['seo'] = SEOGenerator.generate_home_seo(context['profile'], self.request)
        context['structured_data'] = [
            SEOGenerator.generate_structured_data_person(context['profile'], self.request),
            SEOGenerator.generate_structured_data_website(self.request)
        ]

        # Initialize contact form
        if 'contact_form' not in context:
            context['contact_form'] = SecureContactFormWithHoneypot()

        return context

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request, *args, **kwargs):
        form = SecureContactFormWithHoneypot(request.POST)

        if form.is_valid():
            # Check honeypot
            if form.cleaned_data.get('honeypot'):
                logger.warning(f"Honeypot triggered by IP {self.get_client_ip(request)}")
                return redirect('portfolio:home')
                
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            subject = form.cleaned_data.get('subject')
            message = form.cleaned_data.get('message')
            
            try:
                contact = Contact.objects.create(
                    name=name,
                    email=email,
                    subject=subject,
                    message=message
                )
                
                logger.info(f'Contact form submitted by {contact.email} from IP {self.get_client_ip(request)}')
                
                notification_sent = EmailService.send_contact_notification(contact, request.META)
                confirmation_sent = EmailService.send_contact_confirmation(contact)
                
                if notification_sent and confirmation_sent:
                    success_message = _('Thank you for your message! I\'ve sent you a confirmation email and will get back to you soon.')
                elif notification_sent:
                    success_message = _('Thank you for your message! I\'ll get back to you soon.')
                else:
                    success_message = _('Thank you for your message! It has been saved and I\'ll get back to you soon.')
                
                messages.success(request, success_message)
                return redirect('portfolio:home')
                
            except Exception as e:
                logger.error(f'Contact form error: {e}')
                messages.error(request, _('There was an error processing your message. Please try again.'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        
        return self.render_to_response(self.get_context_data(contact_form=form))


# Custom Error Handlers
def custom_404(request, exception):
    """Custom 404 error handler"""
    try:
        profile = Profile.objects.first()
    except Profile.DoesNotExist:
        profile = None
    
    return render(request, '404.html', {
        'profile': profile,
    }, status=404)


def custom_500(request):
    """Custom 500 error handler"""
    try:
        profile = Profile.objects.first()
    except Profile.DoesNotExist:
        profile = None
    
    return render(request, '500.html', {
        'profile': profile,
    }, status=500)


def custom_403(request, exception):
    """Custom 403 error handler"""
    try:
        profile = Profile.objects.first()
    except Profile.DoesNotExist:
        profile = None
    
    return render(request, '403.html', {
        'profile': profile,
    }, status=403)


# SEO Views
def robots_txt(request):
    """Generate robots.txt file"""
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def security_txt(request):
    """Generate security.txt file"""
    lines = [
        "Contact: mailto:security@example.com",
        "Preferred-Languages: en, es",
        "Canonical: https://example.com/.well-known/security.txt",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def manifest_json(request):
    """Generate manifest.json for PWA"""
    manifest = {
        "name": "Portfolio",
        "short_name": "Portfolio",
        "description": "Professional Portfolio",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#000000",
        "icons": [
            {
                "src": "/static/images/icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/static/images/icon-512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    return JsonResponse(manifest)
