"""
Language-specific URLs for the portfolio app.
"""

from django.urls import path
from . import language_views

urlpatterns = [
    path('', language_views.SetLanguageView.as_view(), name='set_language'),
]