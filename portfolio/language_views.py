"""
Language handling views for the portfolio app.
"""

from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import get_language_from_path
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name='dispatch')
class SetLanguageView(View):
    """
    Custom language switcher view.

    Stores the choice in the language cookie, which is what Django reads on
    later requests, and sends the visitor to the URL of that language. Keeping
    the choice in the session instead was the reason a switched language did
    not survive, since Django dropped session-based language detection.
    """

    def post(self, request):
        """Handle language change requests."""
        supported = dict(settings.LANGUAGES)
        language = request.POST.get('language', settings.LANGUAGE_CODE)
        if language not in supported:
            language = settings.LANGUAGE_CODE

        next_url = request.POST.get('next') or '/'
        if not url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            next_url = '/'

        # Drop whatever language prefix the URL carries, then apply the new one.
        # The default language is served without a prefix.
        current_prefix = get_language_from_path(next_url)
        if current_prefix:
            next_url = next_url[len(current_prefix) + 1:]
        if not next_url.startswith('/'):
            next_url = '/' + next_url
        if language != settings.LANGUAGE_CODE:
            next_url = f'/{language}{next_url}'

        response = HttpResponseRedirect(next_url)
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            language,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            secure=settings.LANGUAGE_COOKIE_SECURE,
            httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
            samesite=settings.LANGUAGE_COOKIE_SAMESITE,
        )
        return response
