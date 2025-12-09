import json
from collections import Counter
from django.conf import settings
from django.contrib import messages
from django.db.models import Q, Count
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import translation, timezone
from django.utils.text import slugify
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, View

from ..models import Profile, Experience, Education, Skill, Language, SiteConfiguration, AutoTranslationRecord
from ..forms.profile import SecureExperienceForm, SecureEducationForm, SecureSkillForm
from ..utils.decorators import AdminRequiredMixin
from ..utils.seo import SEOGenerator
from .base import EditingLanguageContextMixin, AutoTranslationStatusMixin


# ============================================================================
# Public Views
# ============================================================================

class ResumeView(TemplateView):
    """Vista de curriculum completo con informacion organizada"""
    template_name = 'portfolio/resume.html'

    def get_context_data(self, **kwargs):
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
        context['certifications'] = education_qs.filter(education_type='certification').annotate(
            sort_date=Coalesce('end_date', 'start_date')
        ).order_by('-sort_date')
        context['online_courses'] = education_qs.filter(education_type='online_course').annotate(
            sort_date=Coalesce('end_date', 'start_date')
        ).order_by('-sort_date')
        context['bootcamps'] = education_qs.filter(education_type__in=['bootcamp', 'workshop']).order_by('-end_date')

        # Calculate Top Institutions for Continuous Learning
        courses_qs = context['online_courses']
        institutions = [c.institution for c in courses_qs if c.institution]
        top_institutions = Counter(institutions).most_common(5)
        context['top_institutions'] = [{'name': name, 'count': count} for name, count in top_institutions]

        skills = Skill.objects.language(current_language).all().order_by('category', '-proficiency')
        skills_by_category = {}
        for skill in skills:
            skills_by_category.setdefault(skill.category, []).append(skill)
        context['skills_by_category'] = skills_by_category

        context['languages'] = (
            Language.objects.active_translations(current_language)
            .order_by('order', 'translations__name')
        )
        
        # Add SEO context
        seo_context = SEOGenerator.generate_resume_seo(context['profile'], self.request)
        context.update(seo_context)
        
        return context


class ResumePDFView(TemplateView):
    template_name = 'portfolio/resume_pdf.html'


# ============================================================================
# Admin - CV Management Hub
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


# ============================================================================
# Admin - Experience Views
# ============================================================================

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


# ============================================================================
# Admin - Education Views
# ============================================================================

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


# ============================================================================
# Admin - Skill Views
# ============================================================================

class SkillListAdminView(AdminRequiredMixin, ListView):
    """Vista de lista de habilidades para administracion"""
    model = Skill
    template_name = 'portfolio/admin/skill_list.html'
    context_object_name = 'skills'
    paginate_by = 20

    def get_queryset(self):
        current_language = translation.get_language() or settings.LANGUAGE_CODE
        queryset = Skill.objects.language(current_language).all().order_by('category', '-proficiency', 'translations__name')

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
    """Vista para eliminar habilidad con confirmación"""
    model = Skill
    template_name = 'portfolio/admin/skill_confirm_delete.html'
    success_url = reverse_lazy('portfolio:admin-skill-list')
    
    def delete(self, request, *args, **kwargs):
        skill = self.get_object()
        name = skill.safe_translation_getter('name') or skill.name
        messages.success(request, f'Habilidad "{name}" eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


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
