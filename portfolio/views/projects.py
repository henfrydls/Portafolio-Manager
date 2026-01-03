from django.conf import settings
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import translation
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView

from ..models import Project, ProjectType, KnowledgeBase, SiteConfiguration
from ..forms.projects import SecureProjectForm, SecureProjectTypeForm, SecureKnowledgeBaseForm
from ..utils.decorators import AdminRequiredMixin
from ..query_optimizations import QueryOptimizer
from ..utils.seo import SEOGenerator
from .base import EditingLanguageContextMixin, AutoTranslationStatusMixin, _build_translation_status_map


# ============================================================================
# Public Views
# ============================================================================

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


# ============================================================================
# Admin Views - Projects
# ============================================================================

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
# Admin Views - Project Types
# ============================================================================

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


# ============================================================================
# Admin Views - Knowledge Bases
# ============================================================================

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
