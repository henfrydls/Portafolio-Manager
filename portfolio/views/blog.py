import os
import uuid
import json
from django.conf import settings
from django.contrib import messages
from django.core.files.storage import default_storage
from django.db.models import Q, Count
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.utils import translation, timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View

from ..models import BlogPost, Category, SiteConfiguration
from ..forms.blog import SecureBlogPostForm, SecureCategoryForm
from ..utils.decorators import AdminRequiredMixin
from ..query_optimizations import QueryOptimizer
from ..utils.seo import SEOGenerator
from ..translation import schedule_auto_translation
from .base import EditingLanguageContextMixin, AutoTranslationStatusMixin, _build_translation_status_map


# ============================================================================
# Public Views
# ============================================================================

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
        from ..models import Profile
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


# ============================================================================
# Admin Views - Blog Posts
# ============================================================================

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
        initial.setdefault('publish_date', timezone.now())
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


# ============================================================================
# Admin Views - Categories
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


# ============================================================================
# Helper Views
# ============================================================================

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
