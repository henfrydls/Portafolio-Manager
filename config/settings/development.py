"""
Development settings for portfolio_managment project.
"""

from .base import *
import sys

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Environment indicator
ENVIRONMENT = 'DEVELOPMENT'

# Print environment on startup
if 'runserver' in sys.argv:
    print("\n" + "="*50)
    print(f"RUNNING IN {ENVIRONMENT} ENVIRONMENT")
    print("="*50 + "\n")

# Get allowed hosts from environment or use defaults
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS_DEV', 'localhost,127.0.0.1,0.0.0.0,testserver').split(',')

# Development session settings - configurable from environment
SESSION_COOKIE_AGE = int(os.environ.get('SESSION_COOKIE_AGE_DEV', 604800))  # Default 1 week
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Persist across browser sessions
SESSION_COOKIE_SECURE = False  # HTTP allowed in development

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_development.sqlite3',
    }
}

# Email configuration for development
# Use SMTP backend to actually send emails
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
# Use EMAIL_HOST_USER as DEFAULT_FROM_EMAIL if not specified (simplifies configuration)
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'noreply@localhost')
EMAIL_TIMEOUT = 60  # Increased timeout for external domains
# Additional settings for better external domain compatibility
EMAIL_USE_LOCALTIME = False
SERVER_EMAIL = EMAIL_HOST_USER

# CSRF trusted origins for development
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://0.0.0.0:8000',
]
# Add custom origins from environment
csrf_origins_env = os.environ.get('CSRF_TRUSTED_ORIGINS_DEV', '')
if csrf_origins_env:
    CSRF_TRUSTED_ORIGINS.extend(csrf_origins_env.split(','))

# Static files configuration for development
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Cache configuration for development (using local memory cache)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'portfolio-dev-cache',
        'TIMEOUT': 300,  # 5 minutes default
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Logging configuration for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'portfolio': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}