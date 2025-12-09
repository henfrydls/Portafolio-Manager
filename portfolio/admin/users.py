from django.contrib import admin
from django.utils.html import format_html
from parler.admin import TranslatableAdmin
from ..models import Profile, Experience, Education, Skill, Language


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
