"""
Custom authentication views for the portfolio app.
"""
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.conf import settings


class CustomLoginView(auth_views.LoginView):
    """
    Custom login view with enhanced security and user experience.
    """
    template_name = 'portfolio/auth/login.html'
    form_class = AuthenticationForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect to admin dashboard after successful login."""
        return reverse_lazy('portfolio:admin-dashboard')
    
    def form_valid(self, form):
        """Add success message and log login."""
        messages.success(self.request, f'¡Bienvenido de vuelta, {form.get_user().first_name or form.get_user().username}!')
        
        # Log successful login
        import logging
        logger = logging.getLogger('portfolio')
        logger.info(f'User {form.get_user().username} logged in successfully from IP {self.get_client_ip()}')
        
        # Set session expiry
        if not self.request.POST.get('remember_me'):
            self.request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        else:
            # Remember me for 30 days
            self.request.session.set_expiry(30 * 24 * 60 * 60)
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Add error message and log failed login attempt."""
        messages.error(self.request, 'Credenciales inválidas. Por favor, verifica tu usuario y contraseña.')
        
        # Log failed login attempt
        import logging
        logger = logging.getLogger('portfolio')
        username = form.data.get('username', 'unknown')
        logger.warning(f'Failed login attempt for username "{username}" from IP {self.get_client_ip()}')
        
        return super().form_invalid(form)
    
    def get_client_ip(self):
        """Get client IP address for logging."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Iniciar Sesión - Admin'
        return context


class CustomLogoutView(auth_views.LogoutView):
    """
    Custom logout view with success message.
    """
    next_page = reverse_lazy('portfolio:home')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, 'Has cerrado sesión correctamente.')
            
            # Log logout
            import logging
            logger = logging.getLogger('portfolio')
            logger.info(f'User {request.user.username} logged out')
        
        return super().dispatch(request, *args, **kwargs)


class SessionStatusView(LoginRequiredMixin, TemplateView):
    """
    AJAX view to check session status and remaining time.
    """
    def get(self, request, *args, **kwargs):
        from django.http import JsonResponse
        
        if not request.user.is_authenticated:
            return JsonResponse({
                'authenticated': False,
                'session_expired': True
            })
        
        # Get session expiry information
        session_age = request.session.get_expiry_age()
        session_expires_at = None
        
        if session_age:
            session_expires_at = (timezone.now() + timezone.timedelta(seconds=session_age)).isoformat()
        
        return JsonResponse({
            'authenticated': True,
            'session_expired': False,
            'session_age': session_age,
            'session_expires_at': session_expires_at,
            'username': request.user.username,
            'is_staff': request.user.is_staff,
            'is_superuser': request.user.is_superuser,
        })


class ExtendSessionView(LoginRequiredMixin, TemplateView):
    """
    AJAX view to extend the current session.
    """
    def post(self, request, *args, **kwargs):
        from django.http import JsonResponse
        
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Not authenticated'
            }, status=401)
        
        # Extend session
        request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        
        # Log session extension
        import logging
        logger = logging.getLogger('portfolio')
        logger.info(f'Session extended for user {request.user.username}')
        
        return JsonResponse({
            'success': True,
            'message': 'Sesión extendida correctamente',
            'new_expiry': (timezone.now() + timezone.timedelta(seconds=settings.SESSION_COOKIE_AGE)).isoformat()
        })


class PasswordChangeView(LoginRequiredMixin, auth_views.PasswordChangeView):
    """
    Custom password change view with enhanced security.
    """
    template_name = 'portfolio/auth/password_change.html'
    success_url = reverse_lazy('portfolio:admin-dashboard')
    
    def form_valid(self, form):
        messages.success(self.request, 'Tu contraseña ha sido cambiada correctamente.')
        
        # Log password change
        import logging
        logger = logging.getLogger('portfolio')
        logger.info(f'Password changed for user {self.request.user.username}')
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Cambiar Contraseña'
        return context
