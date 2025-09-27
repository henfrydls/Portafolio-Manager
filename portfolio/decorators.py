"""
Custom decorators for authentication and authorization in the portfolio app.
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin as DjangoLoginRequiredMixin


def admin_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in and is staff,
    redirecting to the log-in page if necessary.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Debes iniciar sesión para acceder a esta página.')
                return redirect('admin:login')
            
            if not request.user.is_staff:
                messages.error(request, 'No tienes permisos para acceder a esta página.')
                return redirect('portfolio:home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if function:
        return decorator(function)
    return decorator


def superuser_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in and is superuser,
    redirecting to the log-in page if necessary.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Debes iniciar sesión para acceder a esta página.')
                return redirect('admin:login')
            
            if not request.user.is_superuser:
                messages.error(request, 'No tienes permisos de superusuario para acceder a esta página.')
                return redirect('portfolio:home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if function:
        return decorator(function)
    return decorator


class AdminRequiredMixin(DjangoLoginRequiredMixin):
    """
    Mixin for class-based views that requires the user to be authenticated and staff.
    """
    login_url = '/admin/login/'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Debes iniciar sesión para acceder a esta página.')
            return self.handle_no_permission()
        
        if not request.user.is_staff:
            messages.error(request, 'No tienes permisos para acceder a esta página.')
            return redirect('portfolio:home')
        
        return super().dispatch(request, *args, **kwargs)


class SuperuserRequiredMixin(DjangoLoginRequiredMixin):
    """
    Mixin for class-based views that requires the user to be authenticated and superuser.
    """
    login_url = '/admin/login/'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Debes iniciar sesión para acceder a esta página.')
            return self.handle_no_permission()
        
        if not request.user.is_superuser:
            messages.error(request, 'No tienes permisos de superusuario para acceder a esta página.')
            return redirect('portfolio:home')
        
        return super().dispatch(request, *args, **kwargs)


def ajax_login_required(view_func):
    """
    Decorator for AJAX views that checks if user is authenticated.
    Returns JSON response for AJAX requests.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'error': 'Authentication required',
                    'login_url': reverse('admin:login')
                }, status=401)
            else:
                return redirect('admin:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def session_timeout_check(view_func):
    """
    Decorator that checks if the session is about to expire and warns the user.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            from django.utils import timezone
            from django.conf import settings
            
            # Check if session is about to expire (5 minutes warning)
            session_age = request.session.get_expiry_age()
            if session_age and session_age < 300:  # 5 minutes
                messages.warning(
                    request, 
                    'Tu sesión expirará pronto. Guarda tu trabajo y actualiza la página para extender la sesión.'
                )
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view