"""
Base settings for portfolio_managment project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sitemaps',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'portfolio',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'portfolio.security_middleware.SecurityHeadersMiddleware',  # Custom security headers
    #'portfolio.security_middleware.RateLimitMiddleware',  # Rate limiting
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Language detection and setting
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'portfolio.security_middleware.CSRFFailureLoggingMiddleware',  # CSRF logging
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'portfolio.middleware.PageVisitMiddleware',  # Custom middleware para tracking de visitas
    'portfolio.security_middleware.RequestLoggingMiddleware',  # Security logging (last)
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',  # Internationalization context
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'portfolio.context_processors.profile_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'



# Internationalization
LANGUAGE_CODE = 'en'  # Default language is English
TIME_ZONE = 'America/Santo_Domingo'
USE_I18N = True
USE_L10N = True  # Enable localization
USE_TZ = True

# Available languages
LANGUAGES = [
    ('en', 'English'),
    ('es', 'Español'),
]

# Locale paths for translation files
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# For now, we'll use a simpler approach with template tags

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Session configuration (will be overridden in environment-specific settings)
SESSION_COOKIE_AGE = 3600  # 1 hour (default, overridden per environment)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Default, overridden per environment
SESSION_SAVE_EVERY_REQUEST = False  # Only save when session data changes
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'same-origin'

# Authentication settings
AUTH_USER_MODEL = 'auth.User'  # Use default Django user model
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/admin-dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Password validation (enhanced)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Security headers and CSRF protection
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False
CSRF_TRUSTED_ORIGINS = []  # Will be set per environment

# File upload security
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_HANDLERS = [
    'portfolio.file_handlers.SecureFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

# Allowed file types for uploads
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
ALLOWED_DOCUMENT_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt']
BLOCKED_EXTENSIONS = [
    '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar',
    '.sh', '.py', '.php', '.asp', '.aspx', '.jsp', '.pl', '.cgi'
]

# Email configuration will be set per environment
# Contact form email settings
SEND_CONTACT_CONFIRMATIONS = os.environ.get('SEND_CONTACT_CONFIRMATIONS', 'True').lower() == 'true'
EMAIL_TIMEOUT = 30  # seconds

# Page Visit Tracking Configuration
PAGE_VISIT_CLEANUP_FREQUENCY = 1000  # Ejecutar limpieza cada 1000 requests
PAGE_VISIT_RETENTION_DAYS = 180      # Mantener visitas de los últimos 6 meses

# SEO Configuration
SITE_NAME = 'Portfolio Profesional'
BASE_URL = 'http://localhost:8000'  # Will be overridden in production

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
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
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'portfolio': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'portfolio.middleware': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}