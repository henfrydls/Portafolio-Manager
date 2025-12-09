from django.contrib import admin
from django.conf import settings
from django.utils.html import format_html
from django.utils import translation
from parler.admin import TranslatableAdmin
from ..models import BlogPost, Category

@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    """Administración de categorías de posts"""
    list_display = ('name', 'post_count', 'is_active', 'order')
    list_filter = ('is_active', 'created_at')
    search_fields = ('translations__name', 'translations__description')
    ordering = ('order', 'translations__name')
    list_editable = ('order', 'is_active')

    def get_queryset(self, request):
        """Override to avoid duplicate categories (one per translation)"""
        qs = super().get_queryset(request)
        # Use current language to avoid showing duplicates
        language_code = getattr(request, 'LANGUAGE_CODE', None) or translation.get_language() or settings.LANGUAGE_CODE
        return qs.language(language_code).distinct()

    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Configuración', {
            'fields': ('is_active', 'order')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    readonly_fields = ('created_at', 'updated_at', 'post_count')

    def post_count(self, obj):
        """Muestra el número de posts en esta categoría"""
        count = obj.post_count
        if count > 0:
            return format_html('<strong>{}</strong>', count)
        return count
    post_count.short_description = 'Posts'


@admin.register(BlogPost)
class BlogPostAdmin(TranslatableAdmin):
    """Administración de posts del blog"""
    list_display = ('title', 'category_display', 'status', 'featured', 'publish_date', 'reading_time')
    list_filter = ('category', 'status', 'featured', 'publish_date', 'created_at')
    search_fields = ('translations__title', 'translations__content', 'translations__excerpt', 'tags')
    date_hierarchy = 'publish_date'
    ordering = ('-publish_date', '-created_at')

    fieldsets = (
        ('Contenido Principal', {
            'fields': ('title', 'slug', 'excerpt', 'content')
        }),
        ('Multimedia', {
            'fields': ('featured_image', 'image_preview')
        }),
        ('Clasificación', {
            'fields': ('category', 'tags', 'reading_time')
        }),
        ('Publicación', {
            'fields': ('status', 'publish_date', 'featured')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at', 'image_preview')

    def category_display(self, obj):
        """Muestra la categoría"""
        if obj.category:
            return obj.category.name
        return "Sin categoría"
    category_display.short_description = 'Categoría'

    def image_preview(self, obj):
        """Muestra preview de la imagen destacada"""
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="max-height: 150px; max-width: 200px;" />',
                obj.featured_image.url
            )
        return "Sin imagen"
    image_preview.short_description = "Preview de imagen"
    
    actions = ['mark_as_published', 'mark_as_draft', 'mark_as_featured']
    
    def mark_as_published(self, request, queryset):
        """Acción para marcar posts como publicados"""
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} posts marcados como publicados.')
    mark_as_published.short_description = "Marcar como publicado"
    
    def mark_as_draft(self, request, queryset):
        """Acción para marcar posts como borrador"""
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} posts marcados como borrador.')
    mark_as_draft.short_description = "Marcar como borrador"
    
    def mark_as_featured(self, request, queryset):
        """Acción para marcar posts como destacados"""
        updated = queryset.update(featured=True)
        self.message_user(request, f'{updated} posts marcados como destacados.')
    mark_as_featured.short_description = "Marcar como destacado"
