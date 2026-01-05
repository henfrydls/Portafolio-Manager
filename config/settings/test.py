"""
Django settings for testing in CI/CD environments.
"""
import os
from .dev import *  # noqa

# Override settings for testing
DEBUG = False
TEMPLATE_DEBUG = False

# Test database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'test_portfolio'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 0,
    }
}

# Use in-memory cache for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-test-cache',
    }
}

# Speed up password hashing in tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable migrations in tests for speed
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Use console email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['null'],
            'level': 'CRITICAL',
        },
    },
}

# Static and media files for testing
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_test')  # noqa
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_test')  # noqa

# Disable auto-translation in tests
AUTO_TRANSLATION_ENABLED = False

# Redis for testing (if used)
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')

# Security settings for tests
SECRET_KEY = os.environ.get('SECRET_KEY', 'test-secret-key-not-for-production-use-only')
ALLOWED_HOSTS = ['*']
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Disable celery in tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Test-specific middleware (remove some for speed)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Coverage settings
COVERAGE_MODULE_EXCLUDES = [
    'tests$',
    'settings$',
    'urls$',
    'locale$',
    '__pycache__',
    'migrations',
    'fixtures',
]

# Pytest settings
PYTEST_ADDOPTS = [
    '--verbose',
    '--strict-markers',
    '--tb=short',
]
