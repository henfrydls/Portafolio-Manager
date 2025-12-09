"""
Security middleware for additional protection.
"""
import logging
import time
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


logger = logging.getLogger('portfolio')


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses.
    """
    
    def process_response(self, request, response):
        # Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
            "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com "
            "https://fonts.googleapis.com; "
            "style-src 'self' 'unsafe-inline' "
            "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com "
            "https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com "
            "https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        
        # Add security headers
        response['Content-Security-Policy'] = csp_policy
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'same-origin'
        response['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=(), '
            'payment=(), usb=(), magnetometer=(), gyroscope=()'
        )
        
        # Remove server information
        if 'Server' in response:
            del response['Server']
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware to prevent abuse.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Rate limits: (requests, time_window_seconds)
        self.rate_limits = {
            'default': (100, 3600),  # 100 requests per hour
            'login': (5, 300),       # 5 login attempts per 5 minutes
            'contact': (3, 3600),    # 3 contact form submissions per hour
        }
    
    def __call__(self, request):
        # Check rate limit before processing request
        if not self.check_rate_limit(request):
            logger.warning(f'Rate limit exceeded for IP {self.get_client_ip(request)} on {request.path}')
            return HttpResponseForbidden('Rate limit exceeded. Please try again later.')
        
        response = self.get_response(request)
        return response
    
    def check_rate_limit(self, request):
        """
        Check if the request is within rate limits.
        """
        client_ip = self.get_client_ip(request)
        path = request.path
        
        # Determine rate limit type
        limit_type = 'default'
        if 'login' in path:
            limit_type = 'login'
        elif 'contact' in path and request.method == 'POST':
            limit_type = 'contact'
        
        # Get rate limit settings
        max_requests, time_window = self.rate_limits[limit_type]
        
        # Create cache key
        cache_key = f'rate_limit:{limit_type}:{client_ip}'
        
        # Get current request count
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= max_requests:
            return False
        
        # Increment counter
        cache.set(cache_key, current_requests + 1, time_window)
        
        return True
    
    def get_client_ip(self, request):
        """
        Get the client's IP address.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log suspicious requests and security events.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.suspicious_patterns = [
            # SQL injection attempts
            'union select', 'drop table', 'insert into', 'delete from',
            # XSS attempts
            '<script', 'javascript:', 'vbscript:', 'onload=', 'onerror=',
            # Path traversal
            '../', '..\\', '/etc/passwd', '/etc/shadow',
            # Command injection
            '; cat ', '| cat ', '&& cat ', '|| cat ',
            # File inclusion
            'php://input', 'php://filter', 'data://',
        ]
    
    def __call__(self, request):
        start_time = time.time()
        
        # Check for suspicious patterns
        self.check_suspicious_request(request)
        
        response = self.get_response(request)
        
        # Log slow requests
        duration = time.time() - start_time
        if duration > 5.0:  # Log requests taking more than 5 seconds
            logger.warning(
                f'Slow request: {request.method} {request.path} '
                f'took {duration:.2f}s from IP {self.get_client_ip(request)}'
            )
        
        return response
    
    def check_suspicious_request(self, request):
        """
        Check for suspicious patterns in the request.
        """
        client_ip = self.get_client_ip(request)
        
        # Check URL path
        path_lower = request.path.lower()
        for pattern in self.suspicious_patterns:
            if pattern in path_lower:
                logger.warning(
                    f'Suspicious pattern "{pattern}" in URL path from IP {client_ip}: {request.path}'
                )
                break
        
        # Check query parameters
        for key, value in request.GET.items():
            value_lower = str(value).lower()
            for pattern in self.suspicious_patterns:
                if pattern in value_lower:
                    logger.warning(
                        f'Suspicious pattern "{pattern}" in GET parameter "{key}" '
                        f'from IP {client_ip}: {value}'
                    )
                    break
        
        # Check POST data (only for form data, not files)
        if request.method == 'POST' and request.content_type == 'application/x-www-form-urlencoded':
            for key, value in request.POST.items():
                value_lower = str(value).lower()
                for pattern in self.suspicious_patterns:
                    if pattern in value_lower:
                        logger.warning(
                            f'Suspicious pattern "{pattern}" in POST parameter "{key}" '
                            f'from IP {client_ip}: {value[:100]}...'
                        )
                        break
        
        # Check User-Agent for known bad bots
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        bad_bots = ['sqlmap', 'nikto', 'nessus', 'openvas', 'nmap']
        for bot in bad_bots:
            if bot in user_agent:
                logger.warning(f'Suspicious User-Agent from IP {client_ip}: {user_agent}')
                break
    
    def get_client_ip(self, request):
        """
        Get the client's IP address.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CSRFFailureLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log CSRF failures for security monitoring.
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # This will be called before the view is executed
        return None
    
    def process_exception(self, request, exception):
        # Log CSRF failures
        if 'CSRF' in str(exception):
            client_ip = self.get_client_ip(request)
            logger.warning(
                f'CSRF failure from IP {client_ip} on {request.path}: {exception}'
            )
        return None
    
    def get_client_ip(self, request):
        """
        Get the client's IP address.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip