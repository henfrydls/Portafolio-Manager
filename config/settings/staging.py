"""
Staging settings for portfolio_managment project.
"""

from .base import *
import os
import sys

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # Enable debug for staging testing

# Environment indicator
ENVIRONMENT = 'STAGING'

# Print environment on startup
if 'runserver' in sys.argv or 'gunicorn' in sys.argv:
    print("\n" + "="*50)
    print(f"RUNNING IN {ENVIRONMENT} ENVIRONMENT")
    print("="*50 + "\n")

# Get allowed hosts from environment or use defaults
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS_STAGING', 'staging.yourdomain.com,localhost,127.0.0.1').split(',')

# Staging session settings - configurable from environment
SESSION_COOKIE_AGE = int(os.environ.get('SESSION_COOKIE_AGE_STAGING', 43200))  # Default 12 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Allow session persistence
SESSION_COOKIE_SECURE = True  # HTTPS required in staging

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_staging.sqlite3',
    }
}

# Email configuration for staging
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', f'noreply@{os.environ.get("STAGING_DOMAIN", "staging.yourdomain.com")}')

# CSRF trusted origins for staging
staging_domain = os.environ.get('STAGING_DOMAIN', 'staging.yourdomain.com')
CSRF_TRUSTED_ORIGINS = [
    f'https://{staging_domain}',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
# Add custom origins from environment
csrf_origins_env = os.environ.get('CSRF_TRUSTED_ORIGINS_STAGING', '')
if csrf_origins_env:
    CSRF_TRUSTED_ORIGINS.extend(csrf_origins_env.split(','))

# Static files configuration for staging
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

# Security settings for staging (similar to production but less strict)
SECURE_HSTS_SECONDS = 0  # Disabled for staging
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookie security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'  # Less strict than production
CSRF_COOKIE_SAMESITE = 'Lax'

# Additional security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'same-origin'

# Cache configuration for staging
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'staging-cache',
        'TIMEOUT': 300,
    }
}

# Logging configuration for staging
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
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'portfolio_staging.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'portfolio': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}