"""
Production settings for portfolio_managment project.
"""

from .base import *
import os
import sys

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Environment indicator
ENVIRONMENT = 'PRODUCTION'

# Print environment on startup
if 'runserver' in sys.argv or 'gunicorn' in sys.argv:
    print("\n" + "="*50)
    print(f"RUNNING IN {ENVIRONMENT} ENVIRONMENT")
    print("="*50 + "\n")

# Get allowed hosts from environment or use defaults
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS_PROD', 'yourdomain.com,www.yourdomain.com').split(',')

# Production session settings - configurable from environment
SESSION_COOKIE_AGE = int(os.environ.get('SESSION_COOKIE_AGE_PROD', 86400))  # Default 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Allow session persistence

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_production.sqlite3',
    }
}

# Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
# Set DEFAULT_FROM_EMAIL based on environment or domain
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', f'noreply@{os.environ.get("PRODUCTION_DOMAIN", "yourdomain.com")}')

# Static files configuration for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

# Security settings for production
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookie security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SAMESITE = 'Strict'

# Additional security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'same-origin'

# CSRF trusted origins for production
production_domain = os.environ.get('PRODUCTION_DOMAIN', 'yourdomain.com')
CSRF_TRUSTED_ORIGINS = [
    f'https://{production_domain}',
    f'https://www.{production_domain}',
]
# Add custom origins from environment
csrf_origins_env = os.environ.get('CSRF_TRUSTED_ORIGINS_PROD', '')
if csrf_origins_env:
    CSRF_TRUSTED_ORIGINS.extend(csrf_origins_env.split(','))

# Cache configuration for production (using database cache)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
        'TIMEOUT': 300,  # 5 minutes default
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Logging configuration for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'portfolio.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'portfolio': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}