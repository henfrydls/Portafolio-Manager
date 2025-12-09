from django import forms
from django.contrib import admin
from django.conf import settings
from django.utils.html import format_html
from django.urls import reverse
from django.utils import translation
from parler.admin import TranslatableAdmin
from ..models import Project, ProjectType, KnowledgeBase
from ..forms.projects import build_primary_language_choices

class KnowledgeBaseInline(admin.TabularInline):
    """Inline para bases de conocimiento en proyectos"""
    model = Project.knowledge_bases.through
    extra = 1
    verbose_name = "Base de Conocimiento"
    verbose_name_plural = "Bases de Conocimiento"


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(TranslatableAdmin):
    """Administración de bases de conocimiento"""
    list_display = ('translated_name', 'identifier', 'icon_preview', 'color_preview', 'suggestions_status', 'project_count')
    list_filter = ('identifier',)
    search_fields = ('translations__name', 'identifier', 'icon')
    ordering = ('translations__name',)
    readonly_fields = ('suggested_icon_display', 'suggested_color_display')

    fieldsets = (
        ('Información Básica', {
            'fields': ('identifier', 'name')
        }),
        ('Configuración Visual', {
            'fields': ('icon', 'color')
        }),
        ('Sugerencias Automáticas', {
            'fields': ('suggested_icon_display', 'suggested_color_display'),
            'description': 'Sugerencias basadas en el nombre de la base de conocimiento. Usa las acciones para aplicar automáticamente.',
            'classes': ('collapse',)
        })
    )

    actions = ['apply_suggested_icons', 'apply_suggested_colors', 'apply_all_suggestions']

    def translated_name(self, obj):
        """Nombre traducido de la base de conocimiento"""
        return obj.safe_translation_getter('name', any_language=True)
    translated_name.short_description = "Nombre"
    
    def icon_preview(self, obj):
        """Muestra preview del icono actual"""
        if obj.icon:
            return format_html(
                '<i class="{}" style="font-size: 18px; margin-right: 5px;"></i> <code>{}</code>',
                obj.icon, obj.icon
            )
        return "Sin icono"
    icon_preview.short_description = "Icono Actual"
    
    def color_preview(self, obj):
        """Muestra preview del color"""
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; display: inline-block; margin-right: 5px;"></div> <code>{}</code>',
            obj.color, obj.color
        )
    color_preview.short_description = "Color Actual"
    
    def suggestions_status(self, obj):
        """Muestra si hay sugerencias disponibles"""
        suggested_icon = obj.get_suggested_icon()
        suggested_color = obj.get_suggested_color()
        
        has_icon_suggestion = suggested_icon != 'fas fa-code' and obj.icon != suggested_icon
        has_color_suggestion = suggested_color != '#000000' and obj.color != suggested_color
        
        if has_icon_suggestion or has_color_suggestion:
            suggestions = []
            if has_icon_suggestion:
                suggestions.append("icono")
            if has_color_suggestion:
                suggestions.append("color")
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ Sugerencias: {}</span>',
                ", ".join(suggestions)
            )
        return format_html('<span style="color: #6c757d;">Sin sugerencias</span>')
    suggestions_status.short_description = "Sugerencias"
    
    def suggested_icon_display(self, obj):
        """Muestra el icono sugerido"""
        suggested = obj.get_suggested_icon()
        if suggested != 'fas fa-code':  # Solo mostrar si hay una sugerencia específica
            return format_html(
                '<i class="{}" style="font-size: 18px; margin-right: 5px;"></i> <code>{}</code>',
                suggested, suggested
            )
        return "No hay sugerencia específica para esta tecnología"
    suggested_icon_display.short_description = "Icono Sugerido"
    
    def suggested_color_display(self, obj):
        """Muestra el color sugerido"""
        suggested = obj.get_suggested_color()
        if suggested != '#000000':  # Solo mostrar si hay una sugerencia específica
            return format_html(
                '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; display: inline-block; margin-right: 5px;"></div> <code>{}</code>',
                suggested, suggested
            )
        return "No hay sugerencia específica para esta tecnología"
    suggested_color_display.short_description = "Color Sugerido"
    
    def project_count(self, obj):
        """Cuenta proyectos que usan esta tecnología"""
        count = obj.project_set.count()
        if count > 0:
            url = reverse('admin:portfolio_project_changelist') + f'?technologies__id__exact={obj.id}'
            return format_html('<a href="{}">{} proyectos</a>', url, count)
        return "0 proyectos"
    project_count.short_description = "Proyectos"
    
    def apply_suggested_icons(self, request, queryset):
        """Acción para aplicar iconos sugeridos"""
        updated = 0
        for kb in queryset:
            suggested = kb.get_suggested_icon()
            if suggested != 'fas fa-code' and kb.icon != suggested:
                kb.icon = suggested
                kb.save()
                updated += 1

        if updated > 0:
            self.message_user(request, f'{updated} bases de conocimiento actualizadas con iconos sugeridos.')
        else:
            self.message_user(request, 'No hay iconos sugeridos para aplicar en las bases de conocimiento seleccionadas.')
    apply_suggested_icons.short_description = "Aplicar iconos sugeridos"

    def apply_suggested_colors(self, request, queryset):
        """Acción para aplicar colores sugeridos"""
        updated = 0
        for kb in queryset:
            suggested = kb.get_suggested_color()
            if suggested != '#000000' and kb.color != suggested:
                kb.color = suggested
                kb.save()
                updated += 1

        if updated > 0:
            self.message_user(request, f'{updated} bases de conocimiento actualizadas con colores sugeridos.')
        else:
            self.message_user(request, 'No hay colores sugeridos para aplicar en las bases de conocimiento seleccionadas.')
    apply_suggested_colors.short_description = "Aplicar colores sugeridos"

    def apply_all_suggestions(self, request, queryset):
        """Acción para aplicar todas las sugerencias"""
        updated_icons = 0
        updated_colors = 0

        for kb in queryset:
            suggested_icon = kb.get_suggested_icon()
            suggested_color = kb.get_suggested_color()

            if suggested_icon != 'fas fa-code' and kb.icon != suggested_icon:
                kb.icon = suggested_icon
                updated_icons += 1

            if suggested_color != '#000000' and kb.color != suggested_color:
                kb.color = suggested_color
                updated_colors += 1

            if (suggested_icon != 'fas fa-code' and kb.icon != suggested_icon) or \
               (suggested_color != '#000000' and kb.color != suggested_color):
                kb.save()

        messages = []
        if updated_icons > 0:
            messages.append(f'{updated_icons} iconos')
        if updated_colors > 0:
            messages.append(f'{updated_colors} colores')

        if messages:
            self.message_user(request, f'Sugerencias aplicadas: {", ".join(messages)}.')
        else:
            self.message_user(request, 'No hay sugerencias para aplicar en las bases de conocimiento seleccionadas.')
    apply_all_suggestions.short_description = "Aplicar todas las sugerencias"


class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        language_code = translation.get_language() or settings.LANGUAGE_CODE
        current_value = ''
        if self.instance and getattr(self.instance, 'pk', None):
            current_value = self.instance.primary_language or ''
        original_field = self.fields.get('primary_language')
        if original_field:
            help_text = original_field.help_text
            label = original_field.label
            choices, initial_value = build_primary_language_choices(language_code, current_value)
            self.fields['primary_language'] = forms.ChoiceField(
                choices=choices,
                required=False,
                label=label,
                help_text=help_text,
            )
            self.fields['primary_language'].initial = initial_value
            self.fields['primary_language'].widget.attrs.setdefault('class', 'vSelect')


@admin.register(Project)
class ProjectAdmin(TranslatableAdmin):
    """Administración de proyectos"""
    form = ProjectAdminForm
    list_display = ('title', 'project_type_obj', 'visibility', 'is_private_project', 'featured', 'featured_link_status', 'stars_count', 'primary_language', 'created_at')
    list_filter = ('project_type_obj', 'visibility', 'is_private_project', 'featured', 'primary_language', 'created_at')
    search_fields = ('translations__title', 'translations__description', 'translations__detailed_description', 'github_owner', 'primary_language')
    filter_horizontal = ('knowledge_bases',)
    ordering = ('order', '-created_at')

    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'slug', 'project_type_obj', 'description', 'detailed_description')
        }),
        ('GitHub/Visual', {
            'fields': ('github_owner', 'github_url', 'demo_url'),
            'description': 'Información de GitHub'
        }),
        ('Estadísticas', {
            'fields': ('primary_language', 'stars_count', 'forks_count'),
            'description': 'Para proyectos de GitHub se actualizan automáticamente'
        }),
        ('Tipo de Proyecto', {
            'fields': ('is_private_project',),
            'description': 'Marcar si es un proyecto privado/trabajo sin repositorio público'
        }),
        ('Enlaces para Featured Work', {
            'fields': ('featured_link_type', 'featured_link_post', 'featured_link_pdf', 'featured_link_custom'),
            'description': 'Configura qué enlace mostrar cuando este proyecto aparezca en la sección Featured Work'
        }),
        ('Multimedia', {
            'fields': ('image', 'image_preview')
        }),
        ('Configuración', {
            'fields': ('visibility', 'featured', 'order')
        }),
        ('Bases de Conocimiento', {
            'fields': ('knowledge_bases',),
            'description': 'Tecnologías, metodologías y áreas de experticia utilizadas en este proyecto'
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    
    def knowledge_list(self, obj):
        """Muestra lista de bases de conocimiento del proyecto"""
        current_language = translation.get_language()
        kbs = obj.knowledge_bases.language(current_language).all()[:3]  # Mostrar solo las primeras 3
        kb_names = [
            kb.safe_translation_getter('name', any_language=True)
            for kb in kbs
        ]
        if obj.knowledge_bases.count() > 3:
            kb_names.append(f"... (+{obj.knowledge_bases.count() - 3} más)")
        return ", ".join(kb_names) if kb_names else "Sin bases de conocimiento"
    knowledge_list.short_description = "Conocimientos"

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        """
        Use language-scoped queryset to avoid duplicated KnowledgeBase entries caused by translations.
        """
        if db_field.name == 'knowledge_bases':
            language_code = getattr(request, 'LANGUAGE_CODE', None) or translation.get_language() or settings.LANGUAGE_CODE
            queryset = KnowledgeBase.objects.language(language_code).distinct()
            kwargs['queryset'] = queryset
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    
    def image_preview(self, obj):
        """Muestra preview de la imagen del proyecto"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 150px; max-width: 200px;" />',
                obj.image.url
            )
        return "Sin imagen"
    image_preview.short_description = "Preview de imagen"

    def featured_link_status(self, obj):
        """Muestra el estado del enlace para featured work"""
        if obj.featured_link_type == 'none':
            return format_html('<span style="color: #6c757d;">Sin enlace</span>')
        elif obj.has_featured_link():
            icons = {
                'post': '📝',
                'github': '🔗',
                'demo': '🌐',
                'pdf': '📄',
                'custom': '🔗'
            }
            icon = icons.get(obj.featured_link_type, '🔗')
            return format_html(
                '<span style="color: #28a745;">{} {}</span>',
                icon, obj.get_featured_link_type_display()
            )
        else:
            return format_html('<span style="color: #dc3545;">⚠️ Configuración incompleta</span>')
    featured_link_status.short_description = "Enlace Featured"


@admin.register(ProjectType)
class ProjectTypeAdmin(TranslatableAdmin):
    """Administración de tipos de proyectos"""
    list_display = ('translated_name', 'slug', 'project_count', 'is_active', 'order')
    list_filter = ('is_active', 'created_at')
    search_fields = ('translations__name', 'translations__description')
    ordering = ('order', 'translations__name')
    list_editable = ('order', 'is_active')

    def get_queryset(self, request):
        """Override to avoid duplicate project types (one per translation)"""
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

    readonly_fields = ('created_at', 'updated_at', 'project_count')

    def project_count(self, obj):
        """Muestra el número de proyectos de este tipo"""
        count = obj.project_count
        if count > 0:
            return format_html('<strong>{}</strong>', count)
        return count
    project_count.short_description = 'Proyectos'

    def translated_name(self, obj):
        return obj.safe_translation_getter('name', any_language=True)
    translated_name.short_description = "Nombre"
