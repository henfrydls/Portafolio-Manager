"""
URL configuration for portfolio_managment project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap
from portfolio.sitemaps import sitemaps

# Non-translatable URLs (like admin)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/setlang/', include('portfolio.language_urls')),  # Custom language switcher
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# Translatable URLs with language prefix
urlpatterns += i18n_patterns(
    path('', include('portfolio.urls')),
    prefix_default_language=False,  # Don't add /en/ prefix for default language
)

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'portfolio.views.custom_404'
handler500 = 'portfolio.views.custom_500'
handler403 = 'portfolio.views.custom_403'