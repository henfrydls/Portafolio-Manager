from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.http import JsonResponse
from .models import Profile, Project, BlogPost, Technology, Experience, Education, Skill, Contact, PageVisit, Category
from .decorators import AdminRequiredMixin, SuperuserRequiredMixin
from .forms import SecureProfileForm, SecureProjectForm, SecureBlogPostForm, SecureExperienceForm, SecureEducationForm, SecureSkillForm
from .utils import cleanup_old_page_visits

class HomeView(TemplateView):
    """Vista de página principal minimalista con toda la información esencial"""
    template_name = 'portfolio/home.html'
    
    def post(self, request, *args, **kwargs):
        # Manejar el formulario de contacto
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            # Crear el contacto en la base de datos
            Contact.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            
            # Agregar mensaje de éxito
            messages.success(request, 'Thank you for your message! I\'ll get back to you soon.')
            return redirect('portfolio:home')
        else:
            messages.error(request, 'Please fill in all required fields.')
            
        context = self.get_context_data()
        return render(request, self.template_name, context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener perfil (asumimos que hay solo uno)
        try:
            context['profile'] = Profile.objects.first()
        except Profile.DoesNotExist:
            context['profile'] = None
        
        # Obtener contenido destacado mixto (proyectos y posts)
        featured_projects = Project.objects.filter(
            featured=True,
            visibility='public'
        ).order_by('order')

        featured_posts = BlogPost.objects.filter(
            featured=True,
            status='published'
        ).order_by('-publish_date')

        # Combinar y preparar items destacados con metadata
        featured_items = []

        # Agregar proyectos destacados
        for project in featured_projects:
            featured_url = project.get_featured_link_url()
            is_external = project.featured_link_type in ['github', 'demo', 'pdf', 'custom']

            featured_items.append({
                'type': 'project',
                'object': project,
                'title': project.title,
                'description': project.description,
                'image': project.image,
                'url': project.get_absolute_url() if hasattr(project, 'get_absolute_url') else None,
                'external_url': featured_url if is_external else None,
                'featured_url': featured_url,  # Always include the featured URL
                'featured_link_type': project.featured_link_type,
                'featured_icon': project.get_featured_link_icon(),
                'has_featured_link': project.has_featured_link(),
                'date': project.created_at,
                'order': project.order,
                'technologies': project.technologies.all()[:3],
                'is_external': is_external
            })

        # Agregar posts destacados
        for post in featured_posts:
            featured_items.append({
                'type': 'post',
                'object': post,
                'title': post.title,
                'description': post.excerpt or post.content[:200],
                'image': post.featured_image,
                'url': post.get_absolute_url(),
                'external_url': None,
                'date': post.publish_date,
                'order': 999,  # Posts van después de proyectos por defecto
                'category': post.category,
                'reading_time': post.reading_time,
                'is_external': False
            })

        # Ordenar por order primero, luego por fecha (más reciente primero)
        featured_items.sort(key=lambda x: (x['order'], -x['date'].timestamp()))

        # Limitar a máximo 4 items destacados
        context['featured_items'] = featured_items[:4]
        
        # Obtener proyectos con paginación para la sección Work & Projects
        from django.core.paginator import Paginator
        
        projects_queryset = Project.objects.filter(
            visibility='public'
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
        
        # Obtener últimos posts del blog publicados (máximo 5)
        context['latest_posts'] = BlogPost.objects.filter(
            status='published'
        ).order_by('-publish_date')[:5]
        
        # Agregar datos dinámicos para el modal de contacto
        context['projects_count'] = Project.objects.filter(visibility='public').count()
        context['technologies_count'] = Technology.objects.count()
        
        # Calcular años de experiencia basado en la experiencia más antigua
        oldest_experience = Experience.objects.order_by('start_date').first()
        if oldest_experience and oldest_experience.start_date:
            from datetime import date
            years_diff = date.today().year - oldest_experience.start_date.year
            context['experience_years'] = years_diff
        else:
            context['experience_years'] = 5  # Valor por defecto
        
        return context


class ProjectListView(ListView):
    """Vista de lista de proyectos con filtros por tecnología"""
    model = Project
    template_name = 'portfolio/project_list.html'
    context_object_name = 'projects'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Project.objects.filter(visibility='public').order_by('order', '-created_at')
        
        # Filtro por tecnología
        tech_filter = self.request.GET.get('tech')
        if tech_filter:
            queryset = queryset.filter(technologies__name=tech_filter)
        
        # Búsqueda por título o descripción
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener todas las tecnologías para el filtro
        context['technologies'] = Technology.objects.all().order_by('name')
        
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
        # Solo mostrar proyectos públicos
        return Project.objects.filter(visibility='public')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener proyectos relacionados (mismas tecnologías)
        project = self.get_object()
        related_projects = Project.objects.filter(
            visibility='public',
            technologies__in=project.technologies.all()
        ).exclude(id=project.id).distinct()[:3]
        
        context['related_projects'] = related_projects
        
        return context

class ResumeView(TemplateView):
    """Vista de currículum completo con información organizada"""
    template_name = 'portfolio/resume.html'

    def get_context_data(self, **kwargs):
        from django.utils import timezone
        context = super().get_context_data(**kwargs)

        # Obtener perfil
        try:
            context['profile'] = Profile.objects.first()
        except Profile.DoesNotExist:
            context['profile'] = None

        # Agregar fecha de última actualización
        context['last_updated'] = timezone.now()
        
        # Obtener experiencia laboral ordenada por fecha
        context['experiences'] = Experience.objects.all().order_by('-start_date')
        
        # Obtener educación organizada por tipos
        education_qs = Education.objects.all()
        context['formal_education'] = education_qs.filter(
            education_type='formal'
        ).order_by('-start_date')
        context['certifications'] = education_qs.filter(
            education_type='certification'
        ).order_by('-end_date')
        context['online_courses'] = education_qs.filter(
            education_type='online_course'
        ).order_by('-end_date')
        context['bootcamps'] = education_qs.filter(
            education_type__in=['bootcamp', 'workshop']
        ).order_by('-end_date')
        
        # Obtener habilidades categorizadas
        skills = Skill.objects.all().order_by('category', '-proficiency')
        skills_by_category = {}
        for skill in skills:
            if skill.category not in skills_by_category:
                skills_by_category[skill.category] = []
            skills_by_category[skill.category].append(skill)
        context['skills_by_category'] = skills_by_category
        
        return context

class ResumePDFView(TemplateView):
    template_name = 'portfolio/resume_pdf.html'

class BlogListView(ListView):
    """Vista de lista de posts del blog con filtros y paginación"""
    model = BlogPost
    template_name = 'portfolio/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(status='published').order_by('-publish_date')

        # Filtro por categoría
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Filtro por tag
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__icontains=tag)

        # Búsqueda por título o contenido
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(excerpt__icontains=search)
            )

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener perfil (asumimos que hay solo uno)
        try:
            context['profile'] = Profile.objects.first()
        except Profile.DoesNotExist:
            context['profile'] = None

        # Obtener categorías activas para el filtro
        context['categories'] = Category.objects.filter(is_active=True).order_by('order')

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

        return context

class BlogDetailView(DetailView):
    """Vista de detalle de post del blog con tiempo de lectura"""
    model = BlogPost
    template_name = 'portfolio/blog_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        # Solo mostrar posts publicados
        return BlogPost.objects.filter(status='published')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener perfil (asumimos que hay solo uno)
        try:
            context['profile'] = Profile.objects.first()
        except Profile.DoesNotExist:
            context['profile'] = None

        # Obtener posts relacionados con lógica mejorada
        post = self.get_object()
        related_posts = []
        
        # 1. Primero buscar posts de la misma categoría
        if post.category:
            same_category_posts = BlogPost.objects.filter(
                status='published',
                category=post.category
            ).exclude(id=post.id).order_by('-publish_date')[:2]
            related_posts.extend(same_category_posts)
        
        # 2. Si hay tags, buscar posts con tags similares
        if post.tags and len(related_posts) < 3:
            post_tags = [tag.strip().lower() for tag in post.tags.split(',')]
            tag_related_posts = BlogPost.objects.filter(
                status='published'
            ).exclude(id=post.id).exclude(
                id__in=[p.id for p in related_posts]
            )
            
            # Filtrar posts que tengan al menos un tag en común
            matching_posts = []
            for related_post in tag_related_posts:
                if related_post.tags:
                    related_tags = [tag.strip().lower() for tag in related_post.tags.split(',')]
                    if any(tag in post_tags for tag in related_tags):
                        matching_posts.append(related_post)
            
            # Ordenar por fecha y tomar los necesarios
            matching_posts.sort(key=lambda x: x.publish_date, reverse=True)
            needed = 3 - len(related_posts)
            related_posts.extend(matching_posts[:needed])
        
        # 3. Si aún faltan, agregar posts destacados
        if len(related_posts) < 3:
            featured_posts = BlogPost.objects.filter(
                status='published',
                featured=True
            ).exclude(id=post.id).exclude(
                id__in=[p.id for p in related_posts]
            ).order_by('-publish_date')
            
            needed = 3 - len(related_posts)
            related_posts.extend(featured_posts[:needed])
        
        # 4. Finalmente, completar con posts recientes
        if len(related_posts) < 3:
            recent_posts = BlogPost.objects.filter(
                status='published'
            ).exclude(id=post.id).exclude(
                id__in=[p.id for p in related_posts]
            ).order_by('-publish_date')
            
            needed = 3 - len(related_posts)
            related_posts.extend(recent_posts[:needed])

        context['related_posts'] = related_posts[:3]
        
        # Agregar datos dinámicos para el modal de contacto
        context['projects_count'] = Project.objects.filter(visibility='public').count()
        context['technologies_count'] = Technology.objects.count()
        
        # Calcular años de experiencia basado en la experiencia más antigua
        oldest_experience = Experience.objects.order_by('start_date').first()
        if oldest_experience and oldest_experience.start_date:
            from datetime import date
            years_diff = date.today().year - oldest_experience.start_date.year
            context['experience_years'] = years_diff
        else:
            context['experience_years'] = 5  # Valor por defecto

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
        from django.core.mail import send_mail
        from django.conf import settings
        from django.shortcuts import redirect
        from .forms import SecureContactFormWithHoneypot
        import logging
        
        logger = logging.getLogger('portfolio')
        
        form = SecureContactFormWithHoneypot(request.POST)
        
        if form.is_valid():
            try:
                # Guardar mensaje en la base de datos
                contact = form.save()
                
                # Log successful contact form submission
                logger.info(f'Contact form submitted by {contact.email} from IP {self.get_client_ip(request)}')
                
                # Enviar email de notificación (si está configurado)
                try:
                    profile = Profile.objects.first()
                    if profile and profile.email:
                        email_subject = f"Nuevo mensaje de contacto: {contact.subject}"
                        email_message = f"""
Nuevo mensaje recibido:

Nombre: {contact.name}
Email: {contact.email}
Asunto: {contact.subject}

Mensaje:
{contact.message}

---
Este mensaje fue enviado desde el formulario de contacto
IP: {self.get_client_ip(request)}
Fecha: {contact.created_at}
                        """
                        
                        send_mail(
                            email_subject,
                            email_message,
                            settings.DEFAULT_FROM_EMAIL,
                            [profile.email],
                            fail_silently=True,
                        )
                except Exception as e:
                    # Log error but don't fail the contact form
                    logger.error(f'Failed to send contact email: {e}')
                
                messages.success(
                    request, 
                    '¡Gracias por tu mensaje! Te responderé lo antes posible.'
                )
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
            visit_labels.append(visit['day'])
            visit_data.append(visit['visits'])
        
        context['visit_chart_data'] = {
            'labels': visit_labels,
            'data': visit_data
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
        category_stats = BlogPost.objects.filter(
            category__isnull=False
        ).values('category__name').annotate(
            count=Count('id')
        ).order_by('-count')
        context['category_stats'] = category_stats
        
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
class ProfileUpdateView(AdminRequiredMixin, UpdateView):
    """Vista para actualizar información del perfil"""
    model = Profile
    form_class = SecureProfileForm
    template_name = 'portfolio/admin/profile_form.html'
    success_url = reverse_lazy('portfolio:admin-dashboard')
    
    def get_object(self, queryset=None):
        """Obtener o crear el perfil único"""
        from django.conf import settings
        import os

        # Get default values from environment or use template defaults
        default_name = os.environ.get('PROFILE_NAME', 'Your Name')
        default_title = os.environ.get('PROFILE_TITLE', 'Developer')
        default_bio = os.environ.get('PROFILE_BIO', 'Passionate developer creating innovative technology solutions.')
        default_email = os.environ.get('PROFILE_EMAIL', 'contact@yourdomain.com')
        default_location = os.environ.get('PROFILE_LOCATION', 'Your Location')

        profile, created = Profile.objects.get_or_create(
            pk=1,
            defaults={
                'name': default_name,
                'professional_title': default_title,
                'bio': default_bio,
                'email': default_email,
                'location': default_location
            }
        )
        return profile

    def post(self, request, *args, **kwargs):
        """Handle post request including CV deletion"""
        self.object = self.get_object()

        # Check if CV deletion was requested
        if request.POST.get('delete_resume') == 'true':
            if self.object.resume_pdf:
                # Delete the file from storage
                self.object.resume_pdf.delete()
                messages.success(request, 'CV eliminado exitosamente.')
                return redirect(self.success_url)

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar el perfil. Revisa los campos.')
        return super().form_invalid(form)


# Project Management Views
class ProjectListAdminView(AdminRequiredMixin, ListView):
    """Vista de lista de proyectos para administración"""
    model = Project
    template_name = 'portfolio/admin/project_list.html'
    context_object_name = 'projects'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Project.objects.all().order_by('order', '-created_at')
        
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
        return context


class ProjectCreateView(AdminRequiredMixin, CreateView):
    """Vista para crear nuevo proyecto"""
    model = Project
    form_class = SecureProjectForm
    template_name = 'portfolio/admin/project_form.html'
    success_url = reverse_lazy('portfolio:admin-project-list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Proyecto "{form.instance.title}" creado exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el proyecto. Revisa los campos.')
        return super().form_invalid(form)


class ProjectUpdateView(AdminRequiredMixin, UpdateView):
    """Vista para actualizar proyecto existente"""
    model = Project
    form_class = SecureProjectForm
    template_name = 'portfolio/admin/project_form.html'
    success_url = reverse_lazy('portfolio:admin-project-list')
    
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


# Blog Post Management Views
class BlogPostListAdminView(AdminRequiredMixin, ListView):
    """Vista de lista de posts del blog para administración"""
    model = BlogPost
    template_name = 'portfolio/admin/blogpost_list.html'
    context_object_name = 'posts'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = BlogPost.objects.all().order_by('-created_at')
        
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
        context['categories'] = Category.objects.filter(is_active=True).order_by('order', 'name')

        return context


class BlogPostCreateView(AdminRequiredMixin, CreateView):
    """Vista para crear nuevo post del blog"""
    model = BlogPost
    form_class = SecureBlogPostForm
    template_name = 'portfolio/admin/blogpost_form.html'
    success_url = reverse_lazy('portfolio:admin-blog-list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Post "{form.instance.title}" creado exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el post. Revisa los campos.')
        return super().form_invalid(form)


class BlogPostUpdateView(AdminRequiredMixin, UpdateView):
    """Vista para actualizar post del blog existente"""
    model = BlogPost
    form_class = SecureBlogPostForm
    template_name = 'portfolio/admin/blogpost_form.html'
    success_url = reverse_lazy('portfolio:admin-blog-list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Post "{form.instance.title}" actualizado exitosamente.')
        return super().form_valid(form)
    
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
    """Vista de lista de experiencias laborales para administración"""
    model = Experience
    template_name = 'portfolio/admin/experience_list.html'
    context_object_name = 'experiences'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Experience.objects.all().order_by('-start_date', 'order')
        
        # Filtros de búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(company__icontains=search) | 
                Q(position__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_search'] = self.request.GET.get('search', '')
        return context


class ExperienceCreateView(AdminRequiredMixin, CreateView):
    """Vista para crear nueva experiencia laboral"""
    model = Experience
    form_class = SecureExperienceForm
    template_name = 'portfolio/admin/experience_form.html'
    success_url = reverse_lazy('portfolio:admin-experience-list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Experiencia en "{form.instance.company}" creada exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear la experiencia. Revisa los campos.')
        return super().form_invalid(form)


class ExperienceUpdateView(AdminRequiredMixin, UpdateView):
    """Vista para actualizar experiencia laboral existente"""
    model = Experience
    form_class = SecureExperienceForm
    template_name = 'portfolio/admin/experience_form.html'
    success_url = reverse_lazy('portfolio:admin-experience-list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Experiencia en "{form.instance.company}" actualizada exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar la experiencia. Revisa los campos.')
        return super().form_invalid(form)


class ExperienceDeleteView(AdminRequiredMixin, DeleteView):
    """Vista para eliminar experiencia laboral con confirmación"""
    model = Experience
    template_name = 'portfolio/admin/experience_confirm_delete.html'
    success_url = reverse_lazy('portfolio:admin-experience-list')
    
    def delete(self, request, *args, **kwargs):
        experience = self.get_object()
        messages.success(request, f'Experiencia en "{experience.company}" eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


# Education Management Views
class EducationListAdminView(AdminRequiredMixin, ListView):
    """Vista de lista de educación para administración"""
    model = Education
    template_name = 'portfolio/admin/education_list.html'
    context_object_name = 'educations'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Education.objects.all().order_by('-end_date', '-start_date', 'order')
        
        # Filtros de búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(institution__icontains=search) | 
                Q(degree__icontains=search) |
                Q(field_of_study__icontains=search)
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
        return context


class EducationCreateView(AdminRequiredMixin, CreateView):
    """Vista para crear nueva educación"""
    model = Education
    form_class = SecureEducationForm
    template_name = 'portfolio/admin/education_form.html'
    success_url = reverse_lazy('portfolio:admin-education-list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Educación "{form.instance.degree}" creada exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear la educación. Revisa los campos.')
        return super().form_invalid(form)


class EducationUpdateView(AdminRequiredMixin, UpdateView):
    """Vista para actualizar educación existente"""
    model = Education
    form_class = SecureEducationForm
    template_name = 'portfolio/admin/education_form.html'
    success_url = reverse_lazy('portfolio:admin-education-list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Educación "{form.instance.degree}" actualizada exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar la educación. Revisa los campos.')
        return super().form_invalid(form)


class EducationDeleteView(AdminRequiredMixin, DeleteView):
    """Vista para eliminar educación con confirmación"""
    model = Education
    template_name = 'portfolio/admin/education_confirm_delete.html'
    success_url = reverse_lazy('portfolio:admin-education-list')
    
    def delete(self, request, *args, **kwargs):
        education = self.get_object()
        messages.success(request, f'Educación "{education.degree}" eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


# Skill Management Views
class SkillListAdminView(AdminRequiredMixin, ListView):
    """Vista de lista de habilidades para administración"""
    model = Skill
    template_name = 'portfolio/admin/skill_list.html'
    context_object_name = 'skills'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Skill.objects.all().order_by('category', '-proficiency', 'name')
        
        # Filtros de búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(category__icontains=search)
            )
        
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__icontains=category)
        
        proficiency = self.request.GET.get('proficiency')
        if proficiency:
            queryset = queryset.filter(proficiency=proficiency)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_search'] = self.request.GET.get('search', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_proficiency'] = self.request.GET.get('proficiency', '')
        context['proficiency_choices'] = Skill.PROFICIENCY_CHOICES
        # Get unique categories
        context['categories'] = Skill.objects.values_list('category', flat=True).distinct().order_by('category')
        return context


class SkillCreateView(AdminRequiredMixin, CreateView):
    """Vista para crear nueva habilidad"""
    model = Skill
    form_class = SecureSkillForm
    template_name = 'portfolio/admin/skill_form.html'
    success_url = reverse_lazy('portfolio:admin-skill-list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Habilidad "{form.instance.name}" creada exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear la habilidad. Revisa los campos.')
        return super().form_invalid(form)


class SkillUpdateView(AdminRequiredMixin, UpdateView):
    """Vista para actualizar habilidad existente"""
    model = Skill
    form_class = SecureSkillForm
    template_name = 'portfolio/admin/skill_form.html'
    success_url = reverse_lazy('portfolio:admin-skill-list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Habilidad "{form.instance.name}" actualizada exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar la habilidad. Revisa los campos.')
        return super().form_invalid(form)


class SkillDeleteView(AdminRequiredMixin, DeleteView):
    """Vista para eliminar habilidad con confirmación"""
    model = Skill
    template_name = 'portfolio/admin/skill_confirm_delete.html'
    success_url = reverse_lazy('portfolio:admin-skill-list')
    
    def delete(self, request, *args, **kwargs):
        skill = self.get_object()
        messages.success(request, f'Habilidad "{skill.name}" eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)