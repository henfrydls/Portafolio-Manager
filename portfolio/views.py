from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.files.storage import default_storage
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count
from django.db import transaction, DatabaseError
from django.http import JsonResponse
from django.utils import translation
from django.utils.translation import gettext as _
from django.utils.text import slugify
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import get_user_model, authenticate, login as auth_login
import os
import uuid
from django.contrib.contenttypes.models import ContentType
from .models import (
    Profile,
    Project,
    ProjectType,
    BlogPost,
    KnowledgeBase,
    Experience,
    Education,
    Skill,
    Language,
    Contact,
    PageVisit,
    Category,
    SiteConfiguration,
    AutoTranslationRecord,
)
from .decorators import AdminRequiredMixin, SuperuserRequiredMixin
from .forms import (
    SecureProfileForm,
    SecureProjectForm,
    SecureBlogPostForm,
    SecureCategoryForm,
    SecureProjectTypeForm,
    SecureKnowledgeBaseForm,
    SecureExperienceForm,
    SecureEducationForm,
    SecureSkillForm,
    SiteConfigurationForm,
    InitialSetupForm,
)
from .utils import cleanup_old_page_visits
from .query_optimizations import QueryOptimizer
from .seo_utils import SEOGenerator
from .translation import schedule_auto_translation, _run_auto_translation
from django.db.utils import OperationalError, ProgrammingError

LANGUAGE_SESSION_KEY = getattr(translation, 'LANGUAGE_SESSION_KEY', '_language')


class EditingLanguageContextMixin:
    """Provide editing language context and helper notice for admin forms."""

    def _get_editing_language_payload(self):
        config = SiteConfiguration.get_solo()
        editing_code = config.default_language or settings.LANGUAGE_CODE
        language_map = dict(settings.LANGUAGES)
        editing_label = language_map.get(editing_code, editing_code.upper())
        target_codes = config.get_target_languages()
        target_labels = [language_map.get(code, code.upper()) for code in target_codes]
        return editing_code, editing_label, target_labels, target_codes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        editing_code, editing_label, target_labels, target_codes = self._get_editing_language_payload()
        context.setdefault('editing_language_code', editing_code)
        context.setdefault('editing_language_label', editing_label)
        context.setdefault('target_language_labels', target_labels)
        context.setdefault('current_language', editing_code)
        context.setdefault('default_language', editing_code)
        context.setdefault('available_languages', settings.LANGUAGES)
        context.setdefault('target_languages', target_codes)
        context.setdefault('settings_url', reverse('portfolio:admin-site-configuration'))
        return context


class InitialSetupView(FormView):
    """
    Setup wizard to create the first superuser and configure dashboard language.
    """

    template_name = 'portfolio/admin/initial_setup.html'
    form_class = InitialSetupForm
    success_url = reverse_lazy('portfolio:admin-dashboard')

    def dispatch(self, request, *args, **kwargs):
        if self._superuser_exists():
            messages.info(request, _("A superuser is already configured. Please sign in."))
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
            _("Setup complete. Welcome to your dashboard."),
        )
        return super().form_valid(form)

    @staticmethod
    def _superuser_exists():
        try:
            return get_user_model().objects.filter(is_superuser=True).exists()
        except (ProgrammingError, OperationalError, DatabaseError):
            return False


class AutoTranslationStatusMixin(EditingLanguageContextMixin):
    """Provide auto translation records in context for update views."""

    def get_auto_translation_records(self):
        obj = getattr(self, 'object', None)
        if obj is None or obj.pk is None:
            return []
        content_type = ContentType.objects.get_for_model(obj.__class__)
        return AutoTranslationRecord.objects.filter(
            content_type=content_type,
            object_id=obj.pk
        ).order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auto_translation_records' not in context:
            context['auto_translation_records'] = self.get_auto_translation_records()
        config = SiteConfiguration.get_solo()
        context['auto_translation_enabled'] = config.auto_translate_enabled
        context['default_language'] = config.default_language
        context['target_languages'] = config.get_target_languages()
        return context


def _build_translation_status_map(model, objects):
    """Build a per-object translation status overview for dashboard tables."""
    items = list(objects)
    config = SiteConfiguration.get_solo()
    if not items:
        default_language = config.default_language or settings.LANGUAGE_CODE
        return items, {}, config.auto_translate_enabled, default_language
    default_language = config.default_language or settings.LANGUAGE_CODE
    target_languages = [code for code in config.get_target_languages() if code != default_language]
    languages = [default_language] + target_languages
    language_labels = dict(settings.LANGUAGES)

    content_type = ContentType.objects.get_for_model(model)
    object_ids = [item.pk for item in items if item.pk]
    records = AutoTranslationRecord.objects.filter(
        content_type=content_type,
        object_id__in=object_ids,
    )

    record_map = {}
    for record in records:
        record_map.setdefault(record.object_id, {})[record.language_code] = record

    status_map = {}
    for item in items:
        if (
            hasattr(item, '_prefetched_objects_cache')
            and 'translations' in item._prefetched_objects_cache
        ):
            translations_qs = item._prefetched_objects_cache['translations']
            translation_codes = {trans.language_code for trans in translations_qs}
        else:
            translation_codes = set(item.translations.values_list('language_code', flat=True))

        entry_list = []
        for code in languages:
            label = language_labels.get(code, code.upper())
            entry = {
                'code': code.upper(),
                'label': label,
                'role': 'base' if code == default_language else 'target',
            }

            if code == default_language:
                if code in translation_codes:
                    entry['state'] = 'ok'
                    entry['tooltip'] = _('%(language)s content ready (base)') % {'language': label}
                else:
                    entry['state'] = 'missing'
                    entry['tooltip'] = _('%(language)s content missing (base)') % {'language': label}
            else:
                record = record_map.get(item.pk, {}).get(code)
                if code in translation_codes:
                    entry['state'] = 'ok'
                    entry['tooltip'] = _('%(language)s translation ready') % {'language': label}
                elif record:
                    entry['record_status'] = record.status
                    if record.status == AutoTranslationRecord.STATUS_FAILED:
                        entry['state'] = 'failed'
                        error = (record.error_message or '')[:160]
                        if error:
                            entry['tooltip'] = _('%(language)s auto-translation failed: %(error)s') % {
                                'language': label,
                                'error': error,
                            }
                        else:
                            entry['tooltip'] = _('%(language)s auto-translation failed') % {'language': label}
                    elif record.status == AutoTranslationRecord.STATUS_PENDING:
                        entry['state'] = 'pending'
                        entry['tooltip'] = _('%(language)s auto-translation pending') % {'language': label}
                    else:
                        entry['state'] = 'missing'
                        entry['tooltip'] = _('%(language)s translation missing') % {'language': label}
                else:
                    entry['state'] = 'missing'
                    entry['tooltip'] = _('%(language)s translation missing') % {'language': label}
            entry_list.append(entry)

        status_map[item.pk] = entry_list

    return items, status_map, config.auto_translate_enabled, default_language


class HomeView(TemplateView):
    """Vista de página principal minimalista con toda la información esencial"""
    template_name = 'portfolio/home.html'
    
    def post(self, request, *args, **kwargs):
        # Manejar el formulario de contacto
        from .email_service import EmailService
        import logging
        
        logger = logging.getLogger('portfolio')
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            try:
                # Crear el contacto en la base de datos
                contact = Contact.objects.create(
                    name=name,
                    email=email,
                    subject=subject,
                    message=message
                )
                
                # Log successful contact form submission
                logger.info(f'Contact form submitted by {contact.email} from IP {self.get_client_ip(request)}')
                
                # Enviar emails usando el servicio de email
                notification_sent = EmailService.send_contact_notification(contact, request.META)
                confirmation_sent = EmailService.send_contact_confirmation(contact)
                
                # Mensaje de éxito personalizado basado en el estado del email
                if notification_sent and confirmation_sent:
                    success_message = 'Thank you for your message! I\'ve sent you a confirmation email and will get back to you soon.'
                elif notification_sent:
                    success_message = 'Thank you for your message! I\'ll get back to you soon.'
                else:
                    success_message = 'Thank you for your message! It has been saved and I\'ll get back to you soon.'
                
                messages.success(request, success_message)
                return redirect('portfolio:home')
                
            except Exception as e:
                logger.error(f'Contact form error: {e}')
                messages.error(request, 'There was an error processing your message. Please try again.')
        else:
            messages.error(request, 'Please fill in all required fields.')
            
        context = self.get_context_data()
        return render(request, self.template_name, context)
    
    def get_client_ip(self, request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'Unknown')
        return ip
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener perfil optimizado con cache
        profile = QueryOptimizer.get_optimized_profile()
        context['profile'] = profile
        
        # Agregar contexto SEO
        seo_context = SEOGenerator.generate_home_seo(profile, self.request)
        context.update(seo_context)
        
        # Obtener contenido destacado optimizado
        context['featured_items'] = QueryOptimizer.get_featured_items_optimized(limit=4)
        
        # Obtener proyectos con paginación optimizada
        from django.core.paginator import Paginator
        
        # Use optimized query for projects
        current_language = translation.get_language() or settings.LANGUAGE_CODE
        projects_queryset = Project.objects.language(current_language).filter(
            visibility='public'
        ).select_related('project_type_obj').prefetch_related(
            'knowledge_bases'
        ).order_by('order', '-created_at')
        
        # Paginación: 10 proyectos por página
        projects_paginator = Paginator(projects_queryset, 10)
        projects_page = self.request.GET.get('projects_page', 1)
        
        try:
            projects_page_obj = projects_paginator.page(projects_page)
        except:
            projects_page_obj = projects_paginator.page(1)
        
        context['projects'] = projects_page_obj.object_list
        context['projects_page_obj'] = projects_page_obj
        context['projects_paginator'] = projects_paginator
        
        # Obtener últimos posts del blog optimizados
        context['latest_posts'] = QueryOptimizer.get_optimized_blog_posts(
            status='published', 
            limit=5
        )
        
        # Agregar datos dinámicos para el modal de contacto
        context['projects_count'] = Project.objects.filter(visibility='public').count()
        context['knowledge_bases_count'] = KnowledgeBase.objects.count()
        
        # Calcular años de experiencia basado en la experiencia más antigua
        oldest_experience = Experience.objects.order_by('start_date').first()
        if oldest_experience and oldest_experience.start_date:
            from datetime import date
            years_diff = date.today().year - oldest_experience.start_date.year
            context['experience_years'] = years_diff
        else:
            context['experience_years'] = 5  # Valor por defecto
        
        # Agregar datos estructurados
        context['person_structured_data'] = SEOGenerator.generate_structured_data_person(profile, self.request)
        context['website_structured_data'] = SEOGenerator.generate_structured_data_website(self.request)
        
        return context


class ProjectListView(ListView):
    """Vista de lista de proyectos con filtros por tecnologia"""
    model = Project
    template_name = 'portfolio/project_list.html'
    context_object_name = 'projects'
    paginate_by = 12
    
    def get_queryset(self):
        current_language = translation.get_language() or settings.LANGUAGE_CODE
        queryset = Project.objects.language(current_language).filter(
            visibility='public'
        ).select_related('project_type_obj').prefetch_related(
            'knowledge_bases'
        ).order_by('order', '-created_at')

        tech_filter = self.request.GET.get('tech')
        if tech_filter:
            queryset = queryset.filter(
                Q(knowledge_bases__identifier__iexact=tech_filter) |
                Q(knowledge_bases__translations__name__iexact=tech_filter)
            )

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener todas las bases de conocimiento optimizadas para el filtro
        context['knowledge_bases'] = QueryOptimizer.get_optimized_knowledge_bases()
        
        # Mantener filtros en el contexto
        context['current_tech'] = self.request.GET.get('tech', '')
        context['current_search'] = self.request.GET.get('search', '')
        
        return context

class ProjectDetailView(DetailView):
    """Vista de detalle de proyecto individual"""
    model = Project
    template_name = 'portfolio/project_detail.html'
    context_object_name = 'project'
    
    def get_queryset(self):
        current_language = translation.get_language() or settings.LANGUAGE_CODE
        return Project.objects.language(current_language).filter(visibility='public')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_language = translation.get_language() or settings.LANGUAGE_CODE
        project = self.get_object()
        related_projects = Project.objects.language(current_language).filter(
            visibility='public',
            knowledge_bases__in=project.knowledge_bases.all()
        ).exclude(id=project.id).distinct()[:3]

        context['related_projects'] = related_projects
        seo_context = SEOGenerator.generate_project_seo(project, self.request)
        context.update(seo_context)
        
        return context

class ResumeView(TemplateView):
    """Vista de curriculum completo con informacion organizada"""
    template_name = 'portfolio/resume.html'

    def get_context_data(self, **kwargs):
        from django.utils import timezone
        context = super().get_context_data(**kwargs)

        current_language = translation.get_language() or settings.LANGUAGE_CODE

        try:
            context['profile'] = Profile.objects.first()
        except Profile.DoesNotExist:
            context['profile'] = None

        context['last_updated'] = timezone.now()

        context['experiences'] = Experience.objects.language(current_language).all().order_by('-start_date')

        education_qs = Education.objects.language(current_language).all()
        context['formal_education'] = education_qs.filter(education_type='formal').order_by('-start_date')
        context['certifications'] = education_qs.filter(education_type='certification').order_by('-end_date')
        context['online_courses'] = education_qs.filter(education_type='online_course').order_by('-end_date')
        context['bootcamps'] = education_qs.filter(education_type__in=['bootcamp', 'workshop']).order_by('-end_date')

        skills = Skill.objects.language(current_language).all().order_by('category', '-proficiency')
        skills_by_category = {}
        for skill in skills:
            skills_by_category.setdefault(skill.category, []).append(skill)
        context['skills_by_category'] = skills_by_category

        context['languages'] = (
            Language.objects.active_translations(current_language)
            .order_by('order', 'translations__name')
        )
        return context

class ResumePDFView(TemplateView):
    template_name = 'portfolio/resume_pdf.html'

class BlogListView(ListView):
    """Vista de lista de posts del blog con filtros y paginacion"""
    model = BlogPost
    template_name = 'portfolio/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        current_language = translation.get_language() or settings.LANGUAGE_CODE
        queryset = BlogPost.objects.language(current_language).filter(status='published').order_by('-publish_date')

        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__icontains=tag)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(translations__title__icontains=search) |
                Q(translations__content__icontains=search)
            )

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener perfil (asumimos que hay solo uno)
        try:
            context['profile'] = Profile.objects.first()
        except Profile.DoesNotExist:
            context['profile'] = None

        current_language = translation.get_language() or settings.LANGUAGE_CODE

        # Obtener categorías activas para el filtro
        context['categories'] = (
            Category.objects.active_translations(current_language)
            .filter(is_active=True)
            .order_by('order', 'translations__name')[:6]
        )

        # Obtener todos los tags únicos
        all_posts = BlogPost.objects.filter(status='published')
        all_tags = []
        for post in all_posts:
            all_tags.extend(post.get_tags_list())
        context['available_tags'] = sorted(list(set(all_tags)))

        # Mantener filtros en el contexto
        context['current_category'] = self.request.GET.get('category', '')
        context['current_tag'] = self.request.GET.get('tag', '')
        context['current_search'] = self.request.GET.get('search', '')

        # Posts destacados para sidebar
        context['featured_posts'] = BlogPost.objects.filter(
            status='published',
            featured=True
        ).order_by('-publish_date')[:5]

        # Agregar contexto SEO
        category_filter = None
        if context['current_category']:
            try:
                category_filter = Category.objects.get(slug=context['current_category'])
            except Category.DoesNotExist:
                pass
        
        seo_context = SEOGenerator.generate_blog_list_seo(self.request, category_filter)
        context.update(seo_context)

        return context

class BlogDetailView(DetailView):
    """Vista de detalle de post individual"""
    model = BlogPost
    template_name = 'portfolio/blog_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        current_language = translation.get_language() or settings.LANGUAGE_CODE
        return BlogPost.objects.language(current_language).filter(status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        seo_context = SEOGenerator.generate_blog_post_seo(post, self.request)
        context.update(seo_context)
        return context

class ContactView(TemplateView):
    """Vista de contacto con formulario y validación mejorada"""
    template_name = 'portfolio/contact.html'
    
    def get_context_data(self, **kwargs):
        from .forms import SecureContactFormWithHoneypot
        
        context = super().get_context_data(**kwargs)
        
        # Obtener perfil para mostrar información de contacto
        try:
            context['profile'] = Profile.objects.first()
        except Profile.DoesNotExist:
            context['profile'] = None
        
        # Agregar formulario al contexto
        context['form'] = SecureContactFormWithHoneypot()
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Procesar formulario de contacto con validación mejorada"""
        from django.contrib import messages
        from django.shortcuts import redirect
        from .forms import SecureContactFormWithHoneypot
        from .email_service import EmailService
        import logging
        
        logger = logging.getLogger('portfolio')
        
        form = SecureContactFormWithHoneypot(request.POST)
        
        if form.is_valid():
            try:
                # Guardar mensaje en la base de datos
                contact = form.save()
                
                # Log successful contact form submission
                logger.info(f'Contact form submitted by {contact.email} from IP {self.get_client_ip(request)}')
                
                # Enviar emails usando el servicio de email
                notification_sent = EmailService.send_contact_notification(contact, request.META)
                confirmation_sent = EmailService.send_contact_confirmation(contact)
                
                # Mensaje de éxito personalizado basado en el estado del email
                if notification_sent and confirmation_sent:
                    success_message = '¡Gracias por tu mensaje! Te he enviado una confirmación por email y te responderé lo antes posible.'
                elif notification_sent:
                    success_message = '¡Gracias por tu mensaje! Te responderé lo antes posible.'
                else:
                    success_message = '¡Gracias por tu mensaje! Ha sido guardado y te responderé lo antes posible.'
                
                messages.success(request, success_message)
                return redirect('portfolio:home')
                
            except Exception as e:
                logger.error(f'Contact form error: {e}')
                messages.error(
                    request, 
                    'Hubo un error al enviar tu mensaje. Por favor, inténtalo de nuevo.'
                )
        else:
            # Log form validation errors
            logger.warning(f'Contact form validation failed from IP {self.get_client_ip(request)}: {form.errors}')
            
            # Add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
        
        # Return form with errors
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)
    
    def get_client_ip(self, request):
        """Get client IP address for logging."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class AdminDashboardView(AdminRequiredMixin, TemplateView):
    """Vista del dashboard de administración con estadísticas y accesos rápidos"""
    template_name = 'portfolio/admin_dashboard.html'
    
    def get_context_data(self, **kwargs):
        from django.utils import timezone
        from django.db.models import Count
        from datetime import datetime, timedelta
        
        context = super().get_context_data(**kwargs)
        
        # Obtener perfil
        try:
            context['profile'] = Profile.objects.first()
        except Profile.DoesNotExist:
            context['profile'] = None
        
        # Estadísticas básicas - Solo Site Visits, Blog Posts y Messages
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
        ).extra(
            select={'day': 'date(timestamp)'}
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
        
        # Convertir a JSON para el template
        import json
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
        from django.http import JsonResponse
        from .email_service import EmailService
        
        result = EmailService.test_email_configuration()
        
        if result['success']:
            messages.success(request, result['message'])
        else:
            messages.error(request, result['message'])
        
        return JsonResponse(result)


class AnalyticsView(AdminRequiredMixin, TemplateView):
    """Vista de análiticas detalladas con métricas de visitas y gráficos"""
    template_name = 'portfolio/analytics.html'
    
    def get_context_data(self, **kwargs):
        from django.utils import timezone
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        import json
        
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
        daily_visits = PageVisit.objects.filter(
            timestamp__gte=month_ago
        ).extra(
            select={'day': 'date(timestamp)'}
        ).values('day').annotate(
            visits=Count('id')
        ).order_by('day')
        
        # Preparar datos para gráfico de líneas
        visit_chart_labels = []
        visit_chart_data = []
        
        # Crear lista completa de días (incluyendo días sin visitas)
        current_date = month_ago.date()
        daily_visits_dict = {item['day']: item['visits'] for item in daily_visits}
        
        while current_date <= today:
            visit_chart_labels.append(current_date.strftime('%Y-%m-%d'))
            visit_chart_data.append(daily_visits_dict.get(current_date.strftime('%Y-%m-%d'), 0))
            current_date += timedelta(days=1)
        
        context['daily_visits_chart'] = {
            'labels': json.dumps(visit_chart_labels),
            'data': json.dumps(visit_chart_data)
        }
        
        # Visitas por hora del día (últimos 7 días)
        hourly_visits = PageVisit.objects.filter(
            timestamp__gte=week_ago
        ).extra(
            select={'hour': 'strftime("%%H", timestamp)'}
        ).values('hour').annotate(
            visits=Count('id')
        ).order_by('hour')
        
        # Preparar datos para gráfico de barras por hora
        hourly_labels = [f"{i:02d}:00" for i in range(24)]
        hourly_data = [0] * 24
        
        for item in hourly_visits:
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
        monthly_posts = BlogPost.objects.filter(
            created_at__gte=three_months_ago
        ).extra(
            select={'month': 'strftime("%%Y-%%m", created_at)'}
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        context['monthly_posts_chart'] = {
            'labels': json.dumps([item['month'] for item in monthly_posts]),
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
# CRUD VIEWS FOR CONTENT MANAGEMENT
# ============================================================================

# Profile Management Views
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

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


# Project Management Views
class ProjectListAdminView(AdminRequiredMixin, ListView):
    """Vista de lista de proyectos para administración"""
    model = Project
    template_name = 'portfolio/admin/project_list.html'
    context_object_name = 'projects'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = (
            Project.objects.all()
            .prefetch_related('translations', 'knowledge_bases')
            .order_by('order', '-created_at')
        )
        
        # Filtros de búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        visibility = self.request.GET.get('visibility')
        if visibility:
            queryset = queryset.filter(visibility=visibility)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_search'] = self.request.GET.get('search', '')
        context['current_visibility'] = self.request.GET.get('visibility', '')
        projects_list = list(context['projects'])
        projects_list, status_map, auto_enabled, default_language = _build_translation_status_map(
            Project,
            projects_list,
        )
        context['projects'] = projects_list
        context['translation_status_map'] = status_map
        context['translation_auto_enabled'] = auto_enabled
        context['translation_default_language'] = default_language
        return context


class ProjectCreateView(EditingLanguageContextMixin, AdminRequiredMixin, CreateView):
    """Vista para crear nuevo proyecto"""
    model = Project
    form_class = SecureProjectForm
    template_name = 'portfolio/admin/project_form.html'
    success_url = reverse_lazy('portfolio:admin-project-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        config = SiteConfiguration.get_solo()
        language_code = config.default_language or settings.LANGUAGE_CODE
        kwargs['language_code'] = language_code
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Proyecto "{form.instance.title}" creado exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el proyecto. Revisa los campos.')
        return super().form_invalid(form)


class ProjectUpdateView(AutoTranslationStatusMixin, AdminRequiredMixin, UpdateView):
    """Vista para actualizar proyecto existente"""
    model = Project
    form_class = SecureProjectForm
    template_name = 'portfolio/admin/project_form.html'
    success_url = reverse_lazy('portfolio:admin-project-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        config = SiteConfiguration.get_solo()
        language_code = config.default_language or settings.LANGUAGE_CODE
        kwargs['language_code'] = language_code
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Proyecto "{form.instance.title}" actualizado exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar el proyecto. Revisa los campos.')
        return super().form_invalid(form)


class ProjectDeleteView(AdminRequiredMixin, DeleteView):
    """Vista para eliminar proyecto con confirmación"""
    model = Project
    template_name = 'portfolio/admin/project_confirm_delete.html'
    success_url = reverse_lazy('portfolio:admin-project-list')

    def delete(self, request, *args, **kwargs):
        project = self.get_object()
        messages.success(request, f'Proyecto "{project.title}" eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# Catalog Management Views
# ============================================================================

class CategoryListAdminView(AdminRequiredMixin, ListView):
    """Vista de lista de categorías del blog para administración."""

    model = Category
    template_name = 'portfolio/admin/category_list.html'
    context_object_name = 'categories'
    paginate_by = 25

    def get_queryset(self):
        current_language = translation.get_language() or settings.LANGUAGE_CODE
        queryset = (
            Category.objects.active_translations(current_language)
            .order_by('order', 'translations__name')
        )

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(translations__name__icontains=search) |
                Q(translations__description__icontains=search)
            )

        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = list(context['categories'])
        context['categories'] = categories
        ids = [category.pk for category in categories if category.pk]
        if ids:
            counts = (
                BlogPost.objects.filter(category_id__in=ids)
                .values('category_id')
                .annotate(count=Count('id'))
            )
            context['category_post_counts'] = {item['category_id']: item['count'] for item in counts}
        else:
            context['category_post_counts'] = {}

        context['current_search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_language'] = translation.get_language() or settings.LANGUAGE_CODE
        context['available_languages'] = settings.LANGUAGES
        context['total_categories'] = Category.objects.count()
        return context


class CategoryCreateView(EditingLanguageContextMixin, AdminRequiredMixin, CreateView):
    """Vista para crear nuevas categorías."""

    model = Category
    form_class = SecureCategoryForm
    template_name = 'portfolio/admin/category_form.html'
    success_url = reverse_lazy('portfolio:admin-category-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        config = SiteConfiguration.get_solo()
        language_code = config.default_language or settings.LANGUAGE_CODE
        kwargs['language_code'] = language_code
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        name = self.object.safe_translation_getter('name', any_language=True) or self.object.slug
        messages.success(self.request, f'Categoría "{name}" creada exitosamente.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'No se pudo crear la categoría. Revisa los datos proporcionados.')
        return super().form_invalid(form)


class CategoryUpdateView(AutoTranslationStatusMixin, AdminRequiredMixin, UpdateView):
    """Vista para editar categorías existentes."""

    model = Category
    form_class = SecureCategoryForm
    template_name = 'portfolio/admin/category_form.html'
    success_url = reverse_lazy('portfolio:admin-category-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        current_language = translation.get_language() or settings.LANGUAGE_CODE
        kwargs['language_code'] = current_language
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        name = self.object.safe_translation_getter('name', any_language=True) or self.object.slug
        messages.success(self.request, f'Categoría "{name}" actualizada exitosamente.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'No se pudo actualizar la categoría. Revisa los datos proporcionados.')
        return super().form_invalid(form)


class CategoryDeleteView(AdminRequiredMixin, DeleteView):
    """Vista para eliminar categorías."""

    model = Category
    template_name = 'portfolio/admin/category_confirm_delete.html'
    success_url = reverse_lazy('portfolio:admin-category-list')

    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        name = category.safe_translation_getter('name', any_language=True) or category.slug
        messages.success(request, f'Categoría "{name}" eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


class ProjectTypeListAdminView(AdminRequiredMixin, ListView):
    """Vista de lista de tipos de proyecto."""

    model = ProjectType
    template_name = 'portfolio/admin/projecttype_list.html'
    context_object_name = 'project_types'
    paginate_by = 25

    def get_queryset(self):
        current_language = translation.get_language() or settings.LANGUAGE_CODE
        queryset = (
            ProjectType.objects.active_translations(current_language)
            .order_by('order', 'translations__name')
        )

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(translations__name__icontains=search) |
                Q(translations__description__icontains=search)
            )

        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_types = list(context['project_types'])
        context['project_types'] = project_types
        ids = [ptype.pk for ptype in project_types if ptype.pk]
        if ids:
            counts = (
                Project.objects.filter(project_type_obj_id__in=ids)
                .values('project_type_obj_id')
                .annotate(count=Count('id'))
            )
            context['project_type_project_counts'] = {item['project_type_obj_id']: item['count'] for item in counts}
        else:
            context['project_type_project_counts'] = {}

        context['current_search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_language'] = translation.get_language() or settings.LANGUAGE_CODE
        context['available_languages'] = settings.LANGUAGES
        context['total_project_types'] = ProjectType.objects.count()
        return context


class ProjectTypeCreateView(EditingLanguageContextMixin, AdminRequiredMixin, CreateView):
    """Vista para crear nuevos tipos de proyecto."""

    model = ProjectType
    form_class = SecureProjectTypeForm
    template_name = 'portfolio/admin/projecttype_form.html'
    success_url = reverse_lazy('portfolio:admin-projecttype-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        config = SiteConfiguration.get_solo()
        language_code = config.default_language or settings.LANGUAGE_CODE
        kwargs['language_code'] = language_code
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        name = self.object.safe_translation_getter('name', any_language=True) or self.object.slug
        messages.success(self.request, f'Tipo de proyecto "{name}" creado exitosamente.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'No se pudo crear el tipo de proyecto. Revisa los datos proporcionados.')
        return super().form_invalid(form)


class ProjectTypeUpdateView(AutoTranslationStatusMixin, AdminRequiredMixin, UpdateView):
    """Vista para actualizar tipos de proyecto."""

    model = ProjectType
    form_class = SecureProjectTypeForm
    template_name = 'portfolio/admin/projecttype_form.html'
    success_url = reverse_lazy('portfolio:admin-projecttype-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        current_language = translation.get_language() or settings.LANGUAGE_CODE
        kwargs['language_code'] = current_language
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        name = self.object.safe_translation_getter('name', any_language=True) or self.object.slug
        messages.success(self.request, f'Tipo de proyecto "{name}" actualizado exitosamente.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'No se pudo actualizar el tipo de proyecto. Revisa los datos proporcionados.')
        return super().form_invalid(form)


class ProjectTypeDeleteView(AdminRequiredMixin, DeleteView):
    """Vista para eliminar tipos de proyecto."""

    model = ProjectType
    template_name = 'portfolio/admin/projecttype_confirm_delete.html'
    success_url = reverse_lazy('portfolio:admin-projecttype-list')

    def delete(self, request, *args, **kwargs):
        project_type = self.get_object()
        name = project_type.safe_translation_getter('name', any_language=True) or project_type.slug
        messages.success(request, f'Tipo de proyecto "{name}" eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


class KnowledgeBaseListAdminView(AdminRequiredMixin, ListView):
    """Vista de lista de bases de conocimiento."""

    model = KnowledgeBase
    template_name = 'portfolio/admin/knowledgebase_list.html'
    context_object_name = 'knowledge_bases'
    paginate_by = 25

    def get_queryset(self):
        current_language = translation.get_language() or settings.LANGUAGE_CODE
        queryset = (
            KnowledgeBase.objects.language(current_language)
            .all()
            .order_by('translations__name')
        )

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(translations__name__icontains=search) |
                Q(identifier__icontains=search)
            )

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        knowledge_bases = list(context['knowledge_bases'])
        context['knowledge_bases'] = knowledge_bases
        ids = [kb.pk for kb in knowledge_bases if kb.pk]
        if ids:
            counts = (
                Project.objects.filter(knowledge_bases__id__in=ids)
                .values('knowledge_bases')
                .annotate(count=Count('id', distinct=True))
            )
            context['knowledge_base_project_counts'] = {item['knowledge_bases']: item['count'] for item in counts}
        else:
            context['knowledge_base_project_counts'] = {}

        context['current_search'] = self.request.GET.get('search', '')
        context['current_language'] = translation.get_language() or settings.LANGUAGE_CODE
        context['available_languages'] = settings.LANGUAGES
        context['total_knowledge_bases'] = KnowledgeBase.objects.count()
        return context


class KnowledgeBaseCreateView(EditingLanguageContextMixin, AdminRequiredMixin, CreateView):
    """Vista para crear nuevas bases de conocimiento."""

    model = KnowledgeBase
    form_class = SecureKnowledgeBaseForm
    template_name = 'portfolio/admin/knowledgebase_form.html'
    success_url = reverse_lazy('portfolio:admin-knowledgebase-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        config = SiteConfiguration.get_solo()
        language_code = config.default_language or settings.LANGUAGE_CODE
        kwargs['language_code'] = language_code
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        name = self.object.safe_translation_getter('name', any_language=True) or self.object.identifier
        messages.success(self.request, f'Base de conocimiento "{name}" creada exitosamente.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'No se pudo crear la base de conocimiento. Revisa los datos proporcionados.')
        return super().form_invalid(form)


class KnowledgeBaseUpdateView(AutoTranslationStatusMixin, AdminRequiredMixin, UpdateView):
    """Vista para actualizar bases de conocimiento."""

    model = KnowledgeBase
    form_class = SecureKnowledgeBaseForm
    template_name = 'portfolio/admin/knowledgebase_form.html'
    success_url = reverse_lazy('portfolio:admin-knowledgebase-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        current_language = translation.get_language() or settings.LANGUAGE_CODE
        kwargs['language_code'] = current_language
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        name = self.object.safe_translation_getter('name', any_language=True) or self.object.identifier
        messages.success(self.request, f'Base de conocimiento "{name}" actualizada exitosamente.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'No se pudo actualizar la base de conocimiento. Revisa los datos proporcionados.')
        return super().form_invalid(form)


class KnowledgeBaseDeleteView(AdminRequiredMixin, DeleteView):
    """Vista para eliminar bases de conocimiento."""

    model = KnowledgeBase
    template_name = 'portfolio/admin/knowledgebase_confirm_delete.html'
    success_url = reverse_lazy('portfolio:admin-knowledgebase-list')

    def delete(self, request, *args, **kwargs):
        kb = self.get_object()
        name = kb.safe_translation_getter('name', any_language=True) or kb.identifier
        messages.success(request, f'Base de conocimiento "{name}" eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


# Blog Post Management Views
class BlogPostListAdminView(AdminRequiredMixin, ListView):
    """Vista de lista de posts del blog para administración"""
    model = BlogPost
    template_name = 'portfolio/admin/blogpost_list.html'
    context_object_name = 'posts'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = (
            BlogPost.objects.all()
            .prefetch_related('translations')
            .order_by('-created_at')
        )
        
        # Filtros de búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search) |
                Q(excerpt__icontains=search)
            )
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by category instead of post_type
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_category'] = self.request.GET.get('category', '')

        # Use dynamic categories instead of hardcoded POST_TYPES
        from .models import Category
        current_language = translation.get_language() or settings.LANGUAGE_CODE
        context['categories'] = (
            Category.objects.language(current_language)
            .filter(is_active=True)
            .order_by('order', 'translations__name')
        )
        posts_list = list(context['posts'])
        posts_list, status_map, auto_enabled, default_language = _build_translation_status_map(
            BlogPost,
            posts_list,
        )
        context['posts'] = posts_list
        context['translation_status_map'] = status_map
        context['translation_auto_enabled'] = auto_enabled
        context['translation_default_language'] = default_language

        return context


class BlogPostCreateView(EditingLanguageContextMixin, AdminRequiredMixin, CreateView):
    """Vista para crear nuevo post del blog"""
    model = BlogPost
    form_class = SecureBlogPostForm
    template_name = 'portfolio/admin/blogpost_form.html'
    success_url = reverse_lazy('portfolio:admin-blog-list')

    def get_initial(self):
        initial = super().get_initial()
        initial.setdefault('status', 'published')
        try:
            from django.utils import timezone
            initial.setdefault('publish_date', timezone.now())
        except Exception:
            pass
        return initial

    def post(self, request, *args, **kwargs):
        """Handle POST request with multiple submit buttons"""
        self.object = None
        form = self.get_form()

        if form.is_valid():
            # Determine action based on button clicked
            if 'save_draft' in request.POST:
                form.instance.status = 'draft'
            elif 'publish' in request.POST:
                form.instance.status = 'published'

            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, f'Post "{form.instance.title}" creado exitosamente.')
        response = super().form_valid(form)
        if 'publish' in self.request.POST:
            schedule_auto_translation(self.object)
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el post. Revisa los campos.')
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        config = SiteConfiguration.get_solo()
        language_code = config.default_language or settings.LANGUAGE_CODE
        kwargs['language_code'] = language_code
        return kwargs


class BlogPostUpdateView(AutoTranslationStatusMixin, AdminRequiredMixin, UpdateView):
    """Vista para actualizar post del blog existente"""
    model = BlogPost
    form_class = SecureBlogPostForm
    template_name = 'portfolio/admin/blogpost_form.html'
    success_url = reverse_lazy('portfolio:admin-blog-list')

    def post(self, request, *args, **kwargs):
        """Handle POST request with multiple submit buttons"""
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            # Determine action based on button clicked
            if 'save_draft' in request.POST:
                form.instance.status = 'draft'
            elif 'publish' in request.POST:
                form.instance.status = 'published'

            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, f'Post "{form.instance.title}" actualizado exitosamente.')
        response = super().form_valid(form)
        if 'publish' in self.request.POST:
            schedule_auto_translation(self.object)
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar el post. Revisa los campos.')
        return super().form_invalid(form)


class BlogPostDeleteView(AdminRequiredMixin, DeleteView):
    """Vista para eliminar post del blog con confirmación"""
    model = BlogPost
    template_name = 'portfolio/admin/blogpost_confirm_delete.html'
    success_url = reverse_lazy('portfolio:admin-blog-list')
    
    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        messages.success(request, f'Post "{post.title}" eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


# Contact Message Management Views
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


# AJAX Views for Quick Actions
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


class ToggleProjectFeaturedView(AdminRequiredMixin, TemplateView):
    """Vista AJAX para marcar/desmarcar proyecto como destacado"""
    
    def post(self, request, *args, **kwargs):
        project_id = request.POST.get('project_id')
        try:
            project = Project.objects.get(id=project_id)
            project.featured = not project.featured
            project.save()
            return JsonResponse({
                'success': True,
                'featured': project.featured,
                'message': 'Estado actualizado exitosamente.'
            })
        except Project.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Proyecto no encontrado.'
            })


class ToggleBlogPostFeaturedView(AdminRequiredMixin, TemplateView):
    """Vista AJAX para marcar/desmarcar post como destacado"""
    
    def post(self, request, *args, **kwargs):
        post_id = request.POST.get('post_id')
        try:
            post = BlogPost.objects.get(id=post_id)
            post.featured = not post.featured
            post.save()
            return JsonResponse({
                'success': True,
                'featured': post.featured,
                'message': 'Estado actualizado exitosamente.'
            })
        except BlogPost.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Post no encontrado.'
            })


class QuickPublishBlogPostView(AdminRequiredMixin, TemplateView):
    """Vista AJAX para publicar/despublicar post rápidamente"""
    
    def post(self, request, *args, **kwargs):
        post_id = request.POST.get('post_id')
        try:
            post = BlogPost.objects.get(id=post_id)
            if post.status == 'published':
                post.status = 'draft'
                action = 'despublicado'
            else:
                post.status = 'published'
                action = 'publicado'
            post.save()
            return JsonResponse({
                'success': True,
                'status': post.status,
                'message': f'Post {action} exitosamente.'
            })
        except BlogPost.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Post no encontrado.'
            })

# ============================================================================
# CV MANAGEMENT VIEWS - Experience, Education, Skills
# ============================================================================

class CVManagementView(AdminRequiredMixin, TemplateView):
    """Vista hub para gestión de CV con acceso a todas las secciones"""
    template_name = 'portfolio/admin/cv_hub.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas rápidas
        context['stats'] = {
            'total_experiences': Experience.objects.count(),
            'current_job': Experience.objects.filter(current=True).first(),
            'total_education': Education.objects.count(),
            'current_education': Education.objects.filter(current=True).count(),
            'total_skills': Skill.objects.count(),
            'skill_categories': Skill.objects.values_list('category', flat=True).distinct().count(),
        }
        
        # Últimos registros agregados
        context['recent_experiences'] = Experience.objects.order_by('-id')[:3]
        context['recent_education'] = Education.objects.order_by('-id')[:3]
        context['recent_skills'] = Skill.objects.order_by('-id')[:5]
        
        return context

# Experience Management Views
class ExperienceListAdminView(AdminRequiredMixin, ListView):
    """Vista de lista de experiencias laborales para administracion"""
    model = Experience
    template_name = 'portfolio/admin/experience_list.html'
    context_object_name = 'experiences'
    paginate_by = 20

    def get_queryset(self):
        current_language = translation.get_language() or settings.LANGUAGE_CODE
        queryset = Experience.objects.language(current_language).all().order_by('-start_date', 'order')

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(translations__company__icontains=search) |
                Q(translations__position__icontains=search) |
                Q(translations__description__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_search'] = self.request.GET.get('search', '')
        context['current_language'] = translation.get_language() or settings.LANGUAGE_CODE
        context['available_languages'] = settings.LANGUAGES
        return context


class ExperienceCreateView(EditingLanguageContextMixin, AdminRequiredMixin, CreateView):
    """Vista para crear nueva experiencia laboral"""
    model = Experience
    form_class = SecureExperienceForm
    template_name = 'portfolio/admin/experience_form.html'
    success_url = reverse_lazy('portfolio:admin-experience-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        config = SiteConfiguration.get_solo()
        language_code = config.default_language or settings.LANGUAGE_CODE
        kwargs['language_code'] = language_code
        return kwargs

    def form_valid(self, form):
        company = form.instance.safe_translation_getter('company') or form.instance.company
        messages.success(self.request, f'Experiencia en {company} creada exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear la experiencia. Revisa los campos.')
        return super().form_invalid(form)


class ExperienceUpdateView(AutoTranslationStatusMixin, AdminRequiredMixin, UpdateView):
    """Vista para actualizar experiencia laboral existente"""
    model = Experience
    form_class = SecureExperienceForm
    template_name = 'portfolio/admin/experience_form.html'
    success_url = reverse_lazy('portfolio:admin-experience-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        config = SiteConfiguration.get_solo()
        language_code = config.default_language or settings.LANGUAGE_CODE
        kwargs['language_code'] = language_code
        return kwargs

    def form_valid(self, form):
        company = form.instance.safe_translation_getter('company') or form.instance.company
        messages.success(self.request, f'Experiencia en {company} actualizada exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar la experiencia. Revisa los campos.')
        return super().form_invalid(form)


class ExperienceDeleteView(AdminRequiredMixin, DeleteView):
    """Vista para eliminar experiencia laboral con confirmacion"""
    model = Experience
    template_name = 'portfolio/admin/experience_confirm_delete.html'
    success_url = reverse_lazy('portfolio:admin-experience-list')

    def delete(self, request, *args, **kwargs):
        experience = self.get_object()
        company = experience.safe_translation_getter('company') or experience.company
        messages.success(request, f'Experiencia en {company} eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


class EducationListAdminView(AdminRequiredMixin, ListView):
    """Vista de lista de educacion para administracion"""
    model = Education
    template_name = 'portfolio/admin/education_list.html'
    context_object_name = 'educations'
    paginate_by = 20

    def get_queryset(self):
        current_language = translation.get_language() or settings.LANGUAGE_CODE
        queryset = Education.objects.language(current_language).all().order_by('-end_date', '-start_date', 'order')

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(translations__institution__icontains=search) |
                Q(translations__degree__icontains=search) |
                Q(translations__field_of_study__icontains=search)
            )

        education_type = self.request.GET.get('type')
        if education_type:
            queryset = queryset.filter(education_type=education_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_search'] = self.request.GET.get('search', '')
        context['current_type'] = self.request.GET.get('type', '')
        context['education_types'] = Education.EDUCATION_TYPES
        context['current_language'] = translation.get_language() or settings.LANGUAGE_CODE
        context['available_languages'] = settings.LANGUAGES
        return context


class EducationCreateView(EditingLanguageContextMixin, AdminRequiredMixin, CreateView):
    """Vista para crear nueva educacion"""
    model = Education
    form_class = SecureEducationForm
    template_name = 'portfolio/admin/education_form.html'
    success_url = reverse_lazy('portfolio:admin-education-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        config = SiteConfiguration.get_solo()
        language_code = config.default_language or settings.LANGUAGE_CODE
        kwargs['language_code'] = language_code
        return kwargs

    def form_valid(self, form):
        degree = form.instance.safe_translation_getter('degree') or form.instance.degree
        messages.success(self.request, f'Educacion {degree} creada exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear la educacion. Revisa los campos.')
        return super().form_invalid(form)


class EducationUpdateView(AutoTranslationStatusMixin, AdminRequiredMixin, UpdateView):
    """Vista para actualizar educacion existente"""
    model = Education
    form_class = SecureEducationForm
    template_name = 'portfolio/admin/education_form.html'
    success_url = reverse_lazy('portfolio:admin-education-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        config = SiteConfiguration.get_solo()
        language_code = config.default_language or settings.LANGUAGE_CODE
        kwargs['language_code'] = language_code
        return kwargs

    def form_valid(self, form):
        degree = form.instance.safe_translation_getter('degree') or form.instance.degree
        messages.success(self.request, f'Educacion {degree} actualizada exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar la educacion. Revisa los campos.')
        return super().form_invalid(form)


class EducationDeleteView(AdminRequiredMixin, DeleteView):
    """Vista para eliminar educacion con confirmacion"""
    model = Education
    template_name = 'portfolio/admin/education_confirm_delete.html'
    success_url = reverse_lazy('portfolio:admin-education-list')

    def delete(self, request, *args, **kwargs):
        education = self.get_object()
        degree = education.safe_translation_getter('degree') or education.degree
        messages.success(request, f'Educacion {degree} eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


class SkillListAdminView(AdminRequiredMixin, ListView):
    """Vista de lista de habilidades para administracion"""
    model = Skill
    template_name = 'portfolio/admin/skill_list.html'
    context_object_name = 'skills'
    paginate_by = 20

    def get_queryset(self):
        current_language = translation.get_language() or settings.LANGUAGE_CODE
        queryset = Skill.objects.language(current_language).all().order_by('category', '-proficiency', 'name')

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(translations__name__icontains=search) |
                Q(category__icontains=search)
            )

        category_filter = self.request.GET.get('category')
        if category_filter:
            queryset = queryset.filter(category=category_filter)

        proficiency_filter = self.request.GET.get('proficiency')
        if proficiency_filter:
            queryset = queryset.filter(proficiency=proficiency_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_search'] = self.request.GET.get('search', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_proficiency'] = self.request.GET.get('proficiency', '')
        context['proficiency_choices'] = Skill.PROFICIENCY_CHOICES
        context['current_language'] = translation.get_language() or settings.LANGUAGE_CODE
        context['available_languages'] = settings.LANGUAGES
        return context


class SkillCreateView(EditingLanguageContextMixin, AdminRequiredMixin, CreateView):
    """Vista para crear nueva habilidad"""
    model = Skill
    form_class = SecureSkillForm
    template_name = 'portfolio/admin/skill_form.html'
    success_url = reverse_lazy('portfolio:admin-skill-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        config = SiteConfiguration.get_solo()
        language_code = config.default_language or settings.LANGUAGE_CODE
        kwargs['language_code'] = language_code
        return kwargs

    def form_valid(self, form):
        name = form.instance.safe_translation_getter('name') or form.instance.name
        messages.success(self.request, f'Habilidad {name} creada exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear la habilidad. Revisa los campos.')
        return super().form_invalid(form)


class SkillUpdateView(EditingLanguageContextMixin, AdminRequiredMixin, UpdateView):
    """Vista para actualizar habilidad existente"""
    model = Skill
    form_class = SecureSkillForm
    template_name = 'portfolio/admin/skill_form.html'
    success_url = reverse_lazy('portfolio:admin-skill-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        config = SiteConfiguration.get_solo()
        language_code = config.default_language or settings.LANGUAGE_CODE
        kwargs['language_code'] = language_code
        return kwargs

    def form_valid(self, form):
        name = form.instance.safe_translation_getter('name') or form.instance.name
        messages.success(self.request, f'Habilidad {name} actualizada exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar la habilidad. Revisa los campos.')
        return super().form_invalid(form)


class SkillDeleteView(AdminRequiredMixin, DeleteView):
    """Vista para eliminar habilidad con confirmacion"""
    model = Skill
    template_name = 'portfolio/admin/skill_confirm_delete.html'
    success_url = reverse_lazy('portfolio:admin-skill-list')

    def delete(self, request, *args, **kwargs):
        skill = self.get_object()
        name = skill.safe_translation_getter('name') or skill.name
        messages.success(request, f'Habilidad {name} eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


class SkillDeleteView(AdminRequiredMixin, DeleteView):
    """Vista para eliminar habilidad con confirmación"""
    model = Skill
    template_name = 'portfolio/admin/skill_confirm_delete.html'
    success_url = reverse_lazy('portfolio:admin-skill-list')
    
    def delete(self, request, *args, **kwargs):
        skill = self.get_object()
        messages.success(request, f'Habilidad "{skill.name}" eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)

class BlogImageUploadView(AdminRequiredMixin, View):
    """Vista AJAX para subir imágenes del blog"""
    
    def post(self, request, *args, **kwargs):
        try:
            if 'image' not in request.FILES:
                return JsonResponse({
                    'success': False,
                    'message': 'No se encontró ninguna imagen'
                })
            
            image = request.FILES['image']
            
            # Validar tipo de archivo
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if image.content_type not in allowed_types:
                return JsonResponse({
                    'success': False,
                    'message': 'Tipo de archivo no permitido. Use JPG, PNG, GIF o WebP'
                })
            
            # Validar tamaño (máximo 5MB) 
            MAX_IMAGE_SIZE = int(os.environ.get('MAX_IMAGE_SIZE', '5'))
            if image.size > MAX_IMAGE_SIZE * 1024 * 1024:
                return JsonResponse({
                    'success': False,
                    'message': f'La imagen es demasiado grande. Máximo {MAX_IMAGE_SIZE}MB'
                })
            
            # Generar nombre único para el archivo
            ext = os.path.splitext(image.name)[1]
            filename = f"blog/content/{uuid.uuid4()}{ext}"
            
            # Guardar la imagen
            saved_path = default_storage.save(filename, image)
            
            # Obtener la URL completa
            image_url = request.build_absolute_uri(default_storage.url(saved_path))
            
            return JsonResponse({
                'success': True,
                'url': image_url,
                'filename': os.path.basename(saved_path)
            })
            
        except Exception as e:
            import logging
            logger = logging.getLogger('portfolio')
            logger.error(f'Error uploading blog image: {e}')
            
            return JsonResponse({
                'success': False,
                'message': 'Error al procesar la imagen'
            })


# Custom Error Handlers
def custom_404(request, exception):
    """Custom 404 error handler"""
    try:
        profile = Profile.objects.first()
    except Profile.DoesNotExist:
        profile = None
    
    return render(request, '404.html', {
        'profile': profile,
    }, status=404)


def custom_500(request):
    """Custom 500 error handler"""
    try:
        profile = Profile.objects.first()
    except Profile.DoesNotExist:
        profile = None
    
    return render(request, '500.html', {
        'profile': profile,
    }, status=500)


def custom_403(request, exception):
    """Custom 403 error handler"""
    try:
        profile = Profile.objects.first()
    except Profile.DoesNotExist:
        profile = None
    
    return render(request, '403.html', {
        'profile': profile,
    }, status=403)



# ============================================================================
# Language Management API Views
# ============================================================================

class LanguageListAPIView(AdminRequiredMixin, View):
    """API view to list all languages"""
    
    def get(self, request, *args, **kwargs):
        current_language = translation.get_language() or settings.LANGUAGE_CODE
        languages = Language.objects.language(current_language).order_by('order', 'translations__name')
        data = {
            'success': True,
            'languages': [
                {
                    'id': lang.id,
                    'code': lang.code,
                    'name': lang.safe_translation_getter('name', any_language=True),
                    'proficiency': lang.proficiency,
                    'order': lang.order
                }
                for lang in languages
            ]
        }
        return JsonResponse(data)


class LanguageDetailAPIView(AdminRequiredMixin, View):
    """API view to get language details"""
    
    def get(self, request, pk, *args, **kwargs):
        try:
            current_language = translation.get_language() or settings.LANGUAGE_CODE
            language = Language.objects.get(pk=pk)
            language.set_current_language(current_language)
            data = {
                'success': True,
                'id': language.id,
                'code': language.code,
                'name': language.safe_translation_getter('name', any_language=True),
                'proficiency': language.proficiency,
                'order': language.order
            }
            return JsonResponse(data)
        except Language.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Language not found'}, status=404)


class LanguageCreateAPIView(AdminRequiredMixin, View):
    """API view to create a new language"""
    
    def post(self, request, *args, **kwargs):
        import json
        try:
            data = json.loads(request.body)
            current_language = translation.get_language() or settings.LANGUAGE_CODE
            
            # Validate required fields
            if not data.get('name') or not data.get('proficiency'):
                return JsonResponse({
                    'success': False,
                    'error': 'Name and proficiency are required'
                }, status=400)

            code = data.get('code') or slugify(data['name'])
            if not code:
                return JsonResponse({
                    'success': False,
                    'error': 'Unable to generate language code'
                }, status=400)
            
            language = Language(
                code=code,
                proficiency=data['proficiency'],
                order=int(data.get('order', 0))
            )
            language.set_current_language(current_language)
            language.name = data['name']
            language.save()
            
            return JsonResponse({
                'success': True,
                'id': language.id,
                'message': 'Language created successfully'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            import logging
            logger = logging.getLogger('portfolio')
            logger.error(f'Error creating language: {e}')
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


class LanguageUpdateAPIView(AdminRequiredMixin, View):
    """API view to update an existing language"""
    
    def post(self, request, pk, *args, **kwargs):
        import json
        try:
            current_language = translation.get_language() or settings.LANGUAGE_CODE
            language = Language.objects.get(pk=pk)
            data = json.loads(request.body)
            
            # Update fields
            if 'name' in data:
                language.set_current_language(current_language)
                language.name = data['name']
            if 'code' in data and data['code']:
                language.code = data['code']
            if 'proficiency' in data:
                language.proficiency = data['proficiency']
            if 'order' in data:
                language.order = int(data['order'])
            
            language.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Language updated successfully'
            })
            
        except Language.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Language not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            import logging
            logger = logging.getLogger('portfolio')
            logger.error(f'Error updating language: {e}')
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


class LanguageDeleteAPIView(AdminRequiredMixin, View):
    """API view to delete a language"""
    
    def post(self, request, pk, *args, **kwargs):
        try:
            language = Language.objects.get(pk=pk)
            language.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Language deleted successfully'
            })
            
        except Language.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Language not found'}, status=404)
        except Exception as e:
            import logging
            logger = logging.getLogger('portfolio')
            logger.error(f'Error deleting language: {e}')
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# SEO Views
# =============================================================================

def robots_txt(request):
    """Generate robots.txt file"""
    from django.http import HttpResponse
    
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def security_txt(request):
    """Generate security.txt file"""
    from django.http import HttpResponse
    
    lines = [
        "Contact: mailto:security@example.com",
        "Preferred-Languages: en, es",
        "Canonical: https://example.com/.well-known/security.txt",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def manifest_json(request):
    """Generate manifest.json for PWA"""
    from django.http import JsonResponse
    
    manifest = {
        "name": "Portfolio",
        "short_name": "Portfolio",
        "description": "Professional Portfolio",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#000000",
        "icons": [
            {
                "src": "/static/images/icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/static/images/icon-512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    return JsonResponse(manifest)
