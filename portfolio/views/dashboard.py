import json
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login as auth_login
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Count, Q
from django.db.models.functions import TruncDate, ExtractHour, TruncMonth
from django.db.utils import OperationalError, ProgrammingError, DatabaseError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils import translation, timezone
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, DeleteView, View, FormView

from ..models import (
    SiteConfiguration, 
    Profile, 
    PageVisit, 
    BlogPost, 
    Contact, 
    Project, 
    KnowledgeBase, 
    ProjectType, 
    Category
)
from ..forms.config import SiteConfigurationForm, InitialSetupForm
from ..forms.profile import SecureProfileForm
from ..utils.decorators import AdminRequiredMixin
from ..utils.email import EmailService
from ..utils.analytics import cleanup_old_page_visits
from .base import EditingLanguageContextMixin, AutoTranslationStatusMixin

LANGUAGE_SESSION_KEY = getattr(translation, 'LANGUAGE_SESSION_KEY', '_language')


# ============================================================================
# Admin Dashboard & Analytics
# ============================================================================

class AdminDashboardView(AdminRequiredMixin, TemplateView):
    """Vista del dashboard de administración con estadísticas y accesos rápidos"""
    template_name = 'portfolio/admin_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener perfil
        try:
            context['profile'] = Profile.objects.first()
        except Profile.DoesNotExist:
            context['profile'] = None
        
        # Estadísticas básicas
        context['stats'] = {
            'total_posts': BlogPost.objects.count(),
            'published_posts': BlogPost.objects.filter(status='published').count(),
            'draft_posts': BlogPost.objects.filter(status='draft').count(),
            'featured_posts': BlogPost.objects.filter(featured=True).count(),

            'total_messages': Contact.objects.count(),
            'unread_messages': Contact.objects.filter(read=False).count(),
            'read_messages': Contact.objects.filter(read=True).count(),

            'total_visits': PageVisit.objects.count(),
            'total_categories': Category.objects.count(),
            'total_project_types': ProjectType.objects.count(),
            'total_knowledge_bases': KnowledgeBase.objects.count(),
        }
        
        # Estadísticas de visitas por día (últimos 30 días)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_visits = PageVisit.objects.filter(
            timestamp__gte=thirty_days_ago
        ).annotate(
            day=TruncDate('timestamp')
        ).values('day').annotate(
            visits=Count('id')
        ).order_by('day')
        
        # Preparar datos para gráfico de visitas
        visit_data = []
        visit_labels = []
        for visit in daily_visits:
            # Convertir fecha a string para JSON
            day_str = visit['day'].strftime('%Y-%m-%d') if hasattr(visit['day'], 'strftime') else str(visit['day'])
            visit_labels.append(day_str)
            visit_data.append(visit['visits'])
        
        context['visit_chart_data'] = {
            'labels': json.dumps(visit_labels),
            'data': json.dumps(visit_data)
        }
        
        # Páginas más visitadas (últimos 30 días)
        popular_pages = PageVisit.objects.filter(
            timestamp__gte=thirty_days_ago
        ).values('page_url', 'page_title').annotate(
            visits=Count('id')
        ).order_by('-visits')[:10]
        
        context['popular_pages'] = popular_pages
        
        # Últimos mensajes de contacto (5 más recientes)
        context['recent_messages'] = Contact.objects.order_by('-created_at')[:5]
        
        # Últimos posts del blog
        context['recent_posts'] = BlogPost.objects.order_by('-created_at')[:5]

        # Estadísticas de posts por categoría
        current_language = translation.get_language() or settings.LANGUAGE_CODE
        category_stats_qs = BlogPost.objects.filter(
            category__isnull=False,
            category__translations__language_code=current_language
        ).values('category__translations__name').annotate(
            count=Count('id')
        ).order_by('-count')
        context['category_stats'] = [
            {
                'name': item['category__translations__name'],
                'count': item['count']
            }
            for item in category_stats_qs
        ]
        
        # Visitas de hoy
        today = timezone.now().date()
        context['today_visits'] = PageVisit.objects.filter(
            timestamp__date=today
        ).count()
        
        # Visitas de ayer
        yesterday = today - timedelta(days=1)
        context['yesterday_visits'] = PageVisit.objects.filter(
            timestamp__date=yesterday
        ).count()
        
        # Visitas de esta semana
        week_ago = timezone.now() - timedelta(days=7)
        context['week_visits'] = PageVisit.objects.filter(
            timestamp__gte=week_ago
        ).count()
        
        # Mensajes de esta semana
        context['week_messages'] = Contact.objects.filter(
            created_at__gte=week_ago
        ).count()
        
        return context


class AnalyticsView(AdminRequiredMixin, TemplateView):
    """Vista de análiticas detalladas con métricas de visitas y gráficos"""
    template_name = 'portfolio/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener perfil
        try:
            context['profile'] = Profile.objects.first()
        except Profile.DoesNotExist:
            context['profile'] = None
        
        # Definir períodos de tiempo
        now = timezone.now()
        today = now.date()
        yesterday = today - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        three_months_ago = now - timedelta(days=90)
        
        # Estadísticas básicas de visitas
        context['visit_stats'] = {
            'total_visits': PageVisit.objects.count(),
            'today_visits': PageVisit.objects.filter(timestamp__date=today).count(),
            'yesterday_visits': PageVisit.objects.filter(timestamp__date=yesterday).count(),
            'week_visits': PageVisit.objects.filter(timestamp__gte=week_ago).count(),
            'month_visits': PageVisit.objects.filter(timestamp__gte=month_ago).count(),
            'three_months_visits': PageVisit.objects.filter(timestamp__gte=three_months_ago).count(),
        }
        
        # Calcular cambios porcentuales
        last_week_visits = PageVisit.objects.filter(
            timestamp__gte=now - timedelta(days=14),
            timestamp__lt=week_ago
        ).count()
        
        if last_week_visits > 0:
            week_change = ((context['visit_stats']['week_visits'] - last_week_visits) / last_week_visits) * 100
        else:
            week_change = 100 if context['visit_stats']['week_visits'] > 0 else 0
        
        context['visit_stats']['week_change'] = round(week_change, 1)
        
        # Visitas por día (últimos 30 días) - datos más detallados
        daily_visits = (
            PageVisit.objects.filter(timestamp__gte=month_ago)
            .annotate(day=TruncDate('timestamp'))
            .values('day')
            .annotate(visits=Count('id'))
            .order_by('day')
        )
        
        # Preparar datos para gráfico de líneas
        visit_chart_labels = []
        visit_chart_data = []
        
        # Crear lista completa de días (incluyendo días sin visitas)
        current_date = month_ago.date()
        daily_visits_dict = {item['day']: item['visits'] for item in daily_visits}
        
        while current_date <= today:
            visit_chart_labels.append(current_date.strftime('%Y-%m-%d'))
            visit_chart_data.append(daily_visits_dict.get(current_date, 0))
            current_date += timedelta(days=1)
        
        context['daily_visits_chart'] = {
            'labels': json.dumps(visit_chart_labels),
            'data': json.dumps(visit_chart_data)
        }
        
        # Visitas por hora del día (últimos 7 días)
        hourly_visits = (
            PageVisit.objects.filter(timestamp__gte=week_ago)
            .annotate(hour=ExtractHour('timestamp'))
            .values('hour')
            .annotate(visits=Count('id'))
            .order_by('hour')
        )
        
        # Preparar datos para gráfico de barras por hora
        hourly_labels = [f"{i:02d}:00" for i in range(24)]
        hourly_data = [0] * 24
        
        for item in hourly_visits:
            if item['hour'] is None:
                continue
            hour_index = int(item['hour'])
            hourly_data[hour_index] = item['visits']
        
        context['hourly_visits_chart'] = {
            'labels': json.dumps(hourly_labels),
            'data': json.dumps(hourly_data)
        }
        
        # Páginas más visitadas (últimos 30 días) con más detalles
        popular_pages = PageVisit.objects.filter(
            timestamp__gte=month_ago
        ).values('page_url', 'page_title').annotate(
            visits=Count('id')
        ).order_by('-visits')[:15]
        
        context['popular_pages'] = popular_pages
        
        # Análisis de User Agents (navegadores más comunes)
        user_agents = PageVisit.objects.filter(
            timestamp__gte=month_ago
        ).values('user_agent').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Simplificar user agents para mostrar solo el navegador
        browser_stats = {}
        for ua in user_agents:
            browser = self._extract_browser_name(ua['user_agent'])
            if browser in browser_stats:
                browser_stats[browser] += ua['count']
            else:
                browser_stats[browser] = ua['count']
        
        # Convertir a lista ordenada
        browser_list = sorted(browser_stats.items(), key=lambda x: x[1], reverse=True)[:8]
        
        context['browser_chart'] = {
            'labels': json.dumps([item[0] for item in browser_list]),
            'data': json.dumps([item[1] for item in browser_list])
        }
        
        # Estadísticas de contenido
        context['content_stats'] = {
            'total_projects': Project.objects.count(),
            'public_projects': Project.objects.filter(visibility='public').count(),
            'featured_projects': Project.objects.filter(featured=True).count(),
            'total_posts': BlogPost.objects.count(),
            'published_posts': BlogPost.objects.filter(status='published').count(),
            'draft_posts': BlogPost.objects.filter(status='draft').count(),
            'featured_posts': BlogPost.objects.filter(featured=True).count(),
            'total_messages': Contact.objects.count(),
            'unread_messages': Contact.objects.filter(read=False).count(),
        }
        
        # Tendencias de contenido (posts por mes)
        monthly_posts = (
            BlogPost.objects.filter(created_at__gte=three_months_ago)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        
        context['monthly_posts_chart'] = {
            'labels': json.dumps([
                item['month'].strftime('%Y-%m') if item['month'] else ''
                for item in monthly_posts
            ]),
            'data': json.dumps([item['count'] for item in monthly_posts])
        }
        
        # Ejecutar limpieza automática de datos antiguos
        cleanup_old_page_visits()
        
        return context
    
    def _extract_browser_name(self, user_agent):
        """Extrae el nombre del navegador del user agent"""
        user_agent = user_agent.lower()
        
        if 'chrome' in user_agent and 'edg' not in user_agent:
            return 'Chrome'
        elif 'firefox' in user_agent:
            return 'Firefox'
        elif 'safari' in user_agent and 'chrome' not in user_agent:
            return 'Safari'
        elif 'edg' in user_agent:
            return 'Edge'
        elif 'opera' in user_agent or 'opr' in user_agent:
            return 'Opera'
        elif 'bot' in user_agent or 'crawler' in user_agent:
            return 'Bot/Crawler'
        else:
            return 'Other'


# ============================================================================
# Initial Setup & Config Views
# ============================================================================

class InitialSetupView(FormView):
    """
    Setup wizard to create the first superuser and configure dashboard language.
    """

    template_name = 'portfolio/admin/initial_setup.html'
    form_class = InitialSetupForm
    success_url = reverse_lazy('portfolio:admin-dashboard')

    def dispatch(self, request, *args, **kwargs):
        if self._superuser_exists():
            messages.info(request, "A superuser is already configured. Please sign in.")
            return redirect('portfolio:login')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.setdefault('available_languages', settings.LANGUAGES)
        return kwargs

    def form_valid(self, form):
        user = form.save()
        language = form.cleaned_data.get('language') or settings.LANGUAGE_CODE
        translation.activate(language)
        self.request.session[LANGUAGE_SESSION_KEY] = language
        self.request.session['_initial_setup_superuser_present'] = True
        authenticated_user = authenticate(
            self.request,
            username=user.username,
            password=form.cleaned_data.get('password1'),
        )
        if authenticated_user is not None:
            auth_login(self.request, authenticated_user)
        else:
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(self.request, user)
        messages.success(
            self.request,
            "Setup complete. Welcome to your dashboard.",
        )
        return super().form_valid(form)

    @staticmethod
    def _superuser_exists():
        try:
            return get_user_model().objects.filter(is_superuser=True).exists()
        except (ProgrammingError, OperationalError, DatabaseError):
            return False


class SiteConfigurationUpdateView(AdminRequiredMixin, TemplateView):
    """Vista para gestionar la configuración global del sitio."""

    template_name = 'portfolio/admin/site_configuration.html'
    form_class = SiteConfigurationForm

    def get(self, request, *args, **kwargs):
        config = SiteConfiguration.get_solo()
        form = self.form_class(instance=config)
        return self.render_to_response(self.get_context_data(form=form, config=config))

    def post(self, request, *args, **kwargs):
        config = SiteConfiguration.get_solo()
        form = self.form_class(request.POST, instance=config)

        if form.is_valid():
            config = form.save()
            translation.activate(config.default_language)
            request.session[LANGUAGE_SESSION_KEY] = config.default_language
            messages.success(request, 'Configuración actualizada correctamente.')
            return redirect('portfolio:admin-site-configuration')

        messages.error(request, 'No se pudo actualizar la configuración. Revisa los datos e inténtalo de nuevo.')
        return self.render_to_response(self.get_context_data(form=form, config=config))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = kwargs.get('config') or context.get('config') or SiteConfiguration.get_solo()
        context['config'] = config
        context['form'] = kwargs.get('form') or context.get('form') or self.form_class(instance=config)
        context['translation_status'] = self._get_translation_status(config)
        return context

    def _get_translation_status(self, config):
        if not config.auto_translate_enabled:
            return {
                'state': 'disabled',
                'message': 'La traducción automática está desactivada.'
            }
        try:
            service = config.get_translation_service()
        except ImproperlyConfigured as exc:
            return {
                'state': 'error',
                'message': f'Configuración incompleta: {exc}'
            }
        else:
            url = getattr(service, 'api_url', '')
            return {
                'state': 'ok',
                'message': f'{config.get_translation_provider_display()} listo ({url})'
            }


class EmailTestView(AdminRequiredMixin, View):
    """Vista para probar la configuración de email"""
    
    def post(self, request, *args, **kwargs):
        """Enviar email de prueba"""
        from ..utils.email import EmailService  # Local import to avoid circular dependency if email service logic changes
        
        result = EmailService.test_email_configuration()
        
        if result['success']:
            messages.success(request, result['message'])
        else:
            messages.error(request, result['message'])
        
        return JsonResponse(result)


class ProfileUpdateView(AutoTranslationStatusMixin, AdminRequiredMixin, UpdateView):
    """Vista para actualizar información del perfil"""

    model = Profile
    form_class = SecureProfileForm
    template_name = 'portfolio/admin/profile_form.html'
    success_url = reverse_lazy('portfolio:admin-dashboard')

    def get_object(self, queryset=None):
        """Obtener o crear el perfil único (Singleton)"""
        return Profile.get_solo()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        config = SiteConfiguration.get_solo()
        language_code = config.default_language or settings.LANGUAGE_CODE
        kwargs['language_code'] = language_code
        return kwargs

    def post(self, request, *args, **kwargs):
        """Handle post request including CV deletion"""
        self.object = self.get_object()

        # Check if English CV deletion was requested
        if request.POST.get('delete_resume') == 'true':
            if self.object.resume_pdf:
                self.object.resume_pdf.delete()
                messages.success(request, 'English CV deleted successfully.')
                return redirect(self.success_url)

        # Check if Spanish CV deletion was requested
        if request.POST.get('delete_resume_es') == 'true':
            if self.object.resume_pdf_es:
                self.object.resume_pdf_es.delete()
                messages.success(request, 'CV en Español eliminado exitosamente.')
                return redirect(self.success_url)

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar el perfil. Revisa los campos.')
        import logging

        logger = logging.getLogger('portfolio')
        logger.error(f'Profile form errors: {form.errors}')
        return super().form_invalid(form)


# ============================================================================
# Contact Management Views
# ============================================================================

class ContactListAdminView(AdminRequiredMixin, ListView):
    """Vista de lista de mensajes de contacto para administración"""
    model = Contact
    template_name = 'portfolio/admin/contact_list.html'
    context_object_name = 'contacts'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Contact.objects.all().order_by('-created_at')
        
        # Filtros
        status = self.request.GET.get('status')
        if status == 'read':
            queryset = queryset.filter(read=True)
        elif status == 'unread':
            queryset = queryset.filter(read=False)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(email__icontains=search) |
                Q(subject__icontains=search) |
                Q(message__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['unread_count'] = Contact.objects.filter(read=False).count()
        return context


class ContactDetailView(AdminRequiredMixin, DetailView):
    """Vista de detalle de mensaje de contacto"""
    model = Contact
    template_name = 'portfolio/admin/contact_detail.html'
    context_object_name = 'contact'
    
    def get(self, request, *args, **kwargs):
        """Marcar como leído al ver el detalle"""
        response = super().get(request, *args, **kwargs)
        contact = self.get_object()
        if not contact.read:
            contact.read = True
            contact.save()
        return response


class ContactDeleteView(AdminRequiredMixin, DeleteView):
    """Vista para eliminar mensaje de contacto con confirmación"""
    model = Contact
    template_name = 'portfolio/admin/contact_confirm_delete.html'
    success_url = reverse_lazy('portfolio:admin-contact-list')
    
    def delete(self, request, *args, **kwargs):
        contact = self.get_object()
        messages.success(request, f'Mensaje de "{contact.name}" eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


class ToggleContactReadView(AdminRequiredMixin, TemplateView):
    """Vista AJAX para marcar/desmarcar mensaje como leído"""
    
    def post(self, request, *args, **kwargs):
        contact_id = request.POST.get('contact_id')
        try:
            contact = Contact.objects.get(id=contact_id)
            contact.read = not contact.read
            contact.save()
            
            unread_count = Contact.objects.filter(read=False).count()
            
            return JsonResponse({
                'success': True,
                'read': contact.read,
                'unread_count': unread_count,
                'message': 'Estado actualizado exitosamente.'
            })
        except Contact.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Mensaje no encontrado.'
            })
