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
        language = self._requested_language(request)

        response = HttpResponseRedirect(self._safe_next_url(request, language))
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

    @staticmethod
    def _requested_language(request):
        """Return the matching code from settings.LANGUAGES.

        The value that ends up in the cookie comes from the settings tuple and
        never straight from the request.
        """
        requested = request.POST.get('language')
        for code, _name in settings.LANGUAGES:
            if code == requested:
                return code
        return settings.LANGUAGE_CODE

    def _safe_next_url(self, request, language):
        """Where to send the visitor, refusing anything that leaves the site."""
        next_url = request.POST.get('next') or '/'
        if not self._is_internal(request, next_url):
            return self._home_for(language)

        # Drop whatever language prefix the URL carries, then apply the new one.
        # The default language is served without a prefix.
        current_prefix = get_language_from_path(next_url)
        if current_prefix:
            next_url = next_url[len(current_prefix) + 1:]
        if not next_url.startswith('/'):
            next_url = '/' + next_url
        if language != settings.LANGUAGE_CODE:
            next_url = f'/{language}{next_url}'

        # Removing the prefix can turn an accepted path into a scheme-relative
        # URL: '/es//example.com' becomes '//example.com', which a browser
        # reads as another domain. The rebuilt URL is checked again.
        if not self._is_internal(request, next_url):
            return self._home_for(language)
        return next_url

    @staticmethod
    def _is_internal(request, url):
        return url_has_allowed_host_and_scheme(
            url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        )

    @staticmethod
    def _home_for(language):
        return '/' if language == settings.LANGUAGE_CODE else f'/{language}/'
