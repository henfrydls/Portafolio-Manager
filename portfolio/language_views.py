"""
Language handling views for the portfolio app.
"""

from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name='dispatch')
class SetLanguageView(View):
    """
    Custom language switcher view that handles language changes
    and redirects appropriately.
    """

    def post(self, request):
        """Handle language change requests."""
        language = request.POST.get('language', 'en')
        next_url = request.POST.get('next', '/')

        # Store language in session
        request.session['django_language'] = language

        # Clean up the next URL to handle language prefixes
        if next_url.startswith('/es/'):
            next_url = next_url[3:]  # Remove /es/ prefix
        elif next_url.startswith('/en/'):
            next_url = next_url[3:]  # Remove /en/ prefix

        # Add new language prefix if not English (since en is default)
        if language == 'es':
            next_url = f'/es{next_url}'
        else:
            # For English, don't add prefix since it's default
            pass

        # Ensure we have a valid URL
        if not next_url or next_url == '/':
            next_url = '/'

        return HttpResponseRedirect(next_url)