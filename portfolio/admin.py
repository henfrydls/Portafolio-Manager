from django import forms
from django.contrib import admin
from django.conf import settings
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import translation
from parler.admin import TranslatableAdmin
from .models import (
    Profile, KnowledgeBase, Project, Experience, Education,
    Skill, Language, BlogPost, Contact, PageVisit, Category, ProjectType,
    AutoTranslationRecord,
)
from .forms import build_primary_language_choices


class KnowledgeBaseInline(admin.TabularInline):
    """Inline para bases de conocimiento en proyectos"""
    model = Project.knowledge_bases.through
    extra = 1
    verbose_name = "Base de Conocimiento"
    verbose_name_plural = "Bases de Conocimiento"


@admin.register(Profile)
class ProfileAdmin(TranslatableAdmin):
    """Administración del perfil personal (Singleton)"""
    list_display = ('name', 'title', 'email', 'location', 'show_web_resume', 'cv_status', 'updated_at')
    list_filter = ('show_web_resume', 'created_at', 'updated_at')
    search_fields = ('translations__name', 'translations__title', 'email', 'translations__location')
    readonly_fields = ('created_at', 'updated_at', 'profile_image_preview')
    
    def has_add_permission(self, request):
        """Prevent adding more than one profile"""
        return not Profile.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of the profile"""
        return False
    
    fieldsets = (
        ('Personal Information / Información Personal', {
            'fields': ('name', 'title', 'bio', 'profile_image', 'profile_image_preview')
        }),
        ('Contact / Contacto', {
            'fields': ('email', 'phone', 'location')
        }),
        ('Social Links / Enlaces Sociales', {
            'fields': ('linkedin_url', 'github_url', 'medium_url')
        }),
        ('Resume / Currículum', {
            'fields': ('resume_pdf', 'resume_pdf_es', 'show_web_resume'),
            'description': 'Upload your resume in both languages. The system will automatically show the appropriate version based on the visitor\'s language. / Sube tu currículum en ambos idiomas. El sistema mostrará automáticamente la versión apropiada según el idioma del visitante.'
        }),
        ('Metadata / Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def cv_status(self, obj):
        """Shows which CV versions are available"""
        status = []
        if obj.resume_pdf:
            status.append('<span style="color: #28a745;">✓ EN</span>')
        else:
            status.append('<span style="color: #dc3545;">✗ EN</span>')
        
        if obj.resume_pdf_es:
            status.append('<span style="color: #28a745;">✓ ES</span>')
        else:
            status.append('<span style="color: #dc3545;">✗ ES</span>')
        
        return format_html(' | '.join(status))
    cv_status.short_description = "CV Status"
    
    def profile_image_preview(self, obj):
        """Muestra preview de la imagen de perfil"""
        if obj.profile_image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.profile_image.url
            )
        return "Sin imagen"
    profile_image_preview.short_description = "Preview de imagen"


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


@admin.register(Experience)
class ExperienceAdmin(TranslatableAdmin):
    """Administración de experiencia laboral"""
    list_display = ('position', 'company', 'start_date', 'end_date', 'current', 'order')
    list_filter = ('current', 'start_date')
    search_fields = ('translations__company', 'translations__position', 'translations__description')
    ordering = ('-start_date', 'order')
    date_hierarchy = 'start_date'

    fieldsets = (
        ('Información del Trabajo', {
            'fields': ('company', 'position', 'description')
        }),
        ('Fechas', {
            'fields': ('start_date', 'end_date', 'current'),
            'description': 'Si es trabajo actual, marque la casilla y deje vacía la fecha de fin'
        }),
        ('Configuración', {
            'fields': ('order',)
        })
    )


@admin.register(Education)
class EducationAdmin(TranslatableAdmin):
    """Administración de educación"""
    list_display = ('degree', 'institution', 'education_type', 'start_date', 'end_date', 'current')
    list_filter = ('education_type', 'current', 'start_date')
    search_fields = ('translations__institution', 'translations__degree', 'translations__field_of_study', 'translations__description')
    ordering = ('-end_date', '-start_date', 'order')
    date_hierarchy = 'start_date'

    fieldsets = (
        ('Información Académica', {
            'fields': ('institution', 'degree', 'field_of_study', 'education_type')
        }),
        ('Fechas', {
            'fields': ('start_date', 'end_date', 'current'),
            'description': 'Si está en curso, marque la casilla y deje vacía la fecha de fin'
        }),
        ('Detalles Adicionales', {
            'fields': ('description', 'credential_id', 'credential_url'),
            'classes': ('collapse',)
        }),
        ('Configuración', {
            'fields': ('order',)
        })
    )


@admin.register(Skill)
class SkillAdmin(TranslatableAdmin):
    """Administración de habilidades"""
    list_display = ('name', 'category', 'proficiency_display', 'years_experience', 'proficiency_bar')
    list_filter = ('category', 'proficiency', 'years_experience')
    search_fields = ('translations__name', 'category')
    ordering = ('category', '-proficiency', 'translations__name')

    def proficiency_display(self, obj):
        """Muestra el nivel de competencia con texto"""
        return obj.get_proficiency_display()
    proficiency_display.short_description = "Nivel"
    
    def proficiency_bar(self, obj):
        """Muestra barra de progreso visual para el nivel"""
        percentage = (obj.proficiency / 4) * 100  # Calculate percentage directly
        color = {
            1: '#dc3545',  # Rojo para básico
            2: '#ffc107',  # Amarillo para intermedio
            3: '#28a745',  # Verde para avanzado
            4: '#007bff'   # Azul para experto
        }.get(obj.proficiency, '#6c757d')

        return format_html(
            '<div style="width: 100px; background-color: #e9ecef; border-radius: 3px;">'
            '<div style="width: {}%; height: 20px; background-color: {}; border-radius: 3px;"></div>'
            '</div>',
            percentage, color
        )
    proficiency_bar.short_description = "Nivel Visual"


@admin.register(Language)
class LanguageAdmin(TranslatableAdmin):
    """Administración de idiomas"""
    list_display = ('translated_name', 'code', 'proficiency', 'order')
    list_filter = ('proficiency',)
    search_fields = ('translations__name', 'code')
    ordering = ('order', 'translations__name')
    list_editable = ('order',)

    fieldsets = (
        ('Información del Idioma', {
            'fields': ('code', 'name', 'proficiency')
        }),
        ('Configuración', {
            'fields': ('order',)
        })
    )

    def translated_name(self, obj):
        return obj.safe_translation_getter('name', any_language=True)
    translated_name.short_description = "Idioma"


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


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Administración de mensajes de contacto"""
    list_display = ('name', 'email', 'subject', 'created_at', 'read', 'message_preview')
    list_filter = ('read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    def message_preview(self, obj):
        """Muestra preview del mensaje"""
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = "Vista previa del mensaje"
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        """Acción para marcar mensajes como leídos"""
        updated = queryset.update(read=True)
        self.message_user(request, f'{updated} mensajes marcados como leídos.')
    mark_as_read.short_description = "Marcar como leído"
    
    def mark_as_unread(self, request, queryset):
        """Acción para marcar mensajes como no leídos"""
        updated = queryset.update(read=False)
        self.message_user(request, f'{updated} mensajes marcados como no leídos.')
    mark_as_unread.short_description = "Marcar como no leído"
    
    def has_add_permission(self, request):
        """No permitir agregar mensajes desde el admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Solo permitir marcar como leído/no leído"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Permitir eliminar mensajes"""
        return True


@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    """Administración de visitas de páginas"""
    list_display = ('page_url', 'page_title', 'timestamp', 'ip_address', 'user_agent_preview')
    list_filter = ('timestamp', 'page_url')
    search_fields = ('page_url', 'page_title', 'ip_address')
    readonly_fields = ('page_url', 'page_title', 'timestamp', 'ip_address', 'user_agent')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    def user_agent_preview(self, obj):
        """Muestra preview del user agent"""
        return obj.user_agent[:50] + "..." if len(obj.user_agent) > 50 else obj.user_agent
    user_agent_preview.short_description = "User Agent"
    
    def has_add_permission(self, request):
        """No permitir agregar visitas desde el admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir editar visitas"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Permitir eliminar visitas para limpieza"""
        return True
    
    actions = ['delete_old_visits']
    
    def delete_old_visits(self, request, queryset):
        """Acción para eliminar visitas antiguas (más de 6 meses)"""
        from django.utils import timezone
        from datetime import timedelta
        
        six_months_ago = timezone.now() - timedelta(days=180)
        old_visits = PageVisit.objects.filter(timestamp__lt=six_months_ago)
        count = old_visits.count()
        old_visits.delete()
        
        self.message_user(request, f'{count} visitas antiguas eliminadas.')
    delete_old_visits.short_description = "Eliminar visitas antiguas (>6 meses)"


@admin.register(AutoTranslationRecord)
class AutoTranslationRecordAdmin(admin.ModelAdmin):
    """Registro de traducciones automáticas."""
    list_display = (
        'content_object', 'language_code', 'source_language',
        'provider', 'auto_generated', 'status', 'updated_at',
    )
    list_filter = (
        'status', 'auto_generated', 'language_code',
        'source_language', 'provider', 'content_type',
    )
    search_fields = (
        'object_id', 'language_code', 'source_language',
        'provider', 'error_message',
    )
    readonly_fields = (
        'content_type', 'object_id', 'language_code', 'source_language',
        'provider', 'duration_ms', 'auto_generated', 'status',
        'error_message', 'created_at', 'updated_at',
    )
    ordering = ('-updated_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# Personalización del sitio de administración / Admin site customization
admin.site.site_header = "Portfolio Administration / Administración del Portafolio"
admin.site.site_title = "Portfolio Admin"
admin.site.index_title = "Portfolio Management Panel / Panel de Gestión del Portafolio"
