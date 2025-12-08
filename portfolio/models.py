from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.exceptions import ValidationError, ImproperlyConfigured
from parler.models import TranslatableModel, TranslatedFields
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .validators import (
    profile_image_validator, 
    project_image_validator, 
    blog_image_validator, 
    resume_pdf_validator,
    validate_no_executable,
    validate_filename
)
from .image_utils import optimize_uploaded_image
from django.utils import timezone
from django.db import transaction


class SiteConfiguration(models.Model):
    """Singleton storing global preferences for the site."""

    TRANSLATION_PROVIDERS = [
        ('libretranslate', 'LibreTranslate'),
    ]

    default_language = models.CharField(
        max_length=10,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
        verbose_name="Default language"
    )
    auto_translate_enabled = models.BooleanField(
        default=False,
        verbose_name="Enable automatic translation"
    )
    translation_provider = models.CharField(
        max_length=50,
        choices=TRANSLATION_PROVIDERS,
        default=getattr(settings, 'TRANSLATION_PROVIDER', 'libretranslate'),
        verbose_name="Translation provider"
    )
    translation_api_url = models.CharField(
        max_length=255,
        blank=True,
        default=getattr(settings, 'TRANSLATION_API_URL', 'http://libretranslate:5000'),
        verbose_name="Translation service URL"
    )
    translation_api_key = models.CharField(
        max_length=255,
        blank=True,
        default=getattr(settings, 'TRANSLATION_API_KEY', ''),
        verbose_name="Translation service API key"
    )
    translation_timeout = models.PositiveIntegerField(
        default=10,
        verbose_name="Tiempo de espera (segundos)"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site configuration"
        verbose_name_plural = "Site configuration"

    def __str__(self):
        return "Site configuration"

    def save(self, *args, **kwargs):
        if not self.pk and SiteConfiguration.objects.exists():
            raise ValidationError('Only one site configuration instance is allowed.')
        return super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        changed = False
        if not obj.translation_provider:
            obj.translation_provider = getattr(settings, 'TRANSLATION_PROVIDER', 'libretranslate')
            changed = True
        if not obj.translation_api_url:
            obj.translation_api_url = getattr(settings, 'TRANSLATION_API_URL', 'http://libretranslate:5000')
            changed = True
        if obj.translation_api_key is None:
            obj.translation_api_key = getattr(settings, 'TRANSLATION_API_KEY', '')
            changed = True
        if changed:
            obj.save(update_fields=['translation_provider', 'translation_api_url', 'translation_api_key', 'updated_at'])
        return obj

    def get_translation_service(self):
        """Build TranslationService if auto translation is enabled and configured."""
        if not self.auto_translate_enabled:
            return None
        if not self.translation_api_url:
            raise ImproperlyConfigured("Translation API URL is required for auto translation.")
        from .services.translation_service import TranslationService  # lazy import
        return TranslationService(
            provider=self.translation_provider,
            api_url=self.translation_api_url,
            api_key=self.translation_api_key or "",
            timeout=self.translation_timeout,
        )

    def get_target_languages(self):
        default = self.default_language or settings.LANGUAGE_CODE
        return [code for code, _ in settings.LANGUAGES if code != default]


class AutoTranslationRecord(models.Model):
    """Track automatically generated translations."""

    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendiente'),
        (STATUS_SUCCESS, 'Completado'),
        (STATUS_FAILED, 'Fallido'),
    ]

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    language_code = models.CharField(max_length=10)
    source_language = models.CharField(max_length=10)
    provider = models.CharField(max_length=50, blank=True)
    duration_ms = models.PositiveIntegerField(default=0)
    auto_generated = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('content_type', 'object_id', 'language_code')
        verbose_name = 'Registro de traducción automática'
        verbose_name_plural = 'Registros de traducción automática'
        ordering = ['-updated_at']

    def mark_success(self, provider: str, duration_ms: int):
        self.provider = provider
        self.duration_ms = duration_ms
        self.auto_generated = True
        self.status = self.STATUS_SUCCESS
        self.error_message = ''
        self.save(update_fields=['provider', 'duration_ms', 'auto_generated', 'status', 'error_message', 'updated_at'])

    def mark_failure(self, message: str):
        self.auto_generated = False
        self.status = self.STATUS_FAILED
        self.error_message = message[:1000]
        self.save(update_fields=['auto_generated', 'status', 'error_message', 'updated_at'])


class Profile(TranslatableModel):
    """Modelo para información personal del portafolio (Singleton)"""

    translations = TranslatedFields(
        name=models.CharField(max_length=100, verbose_name="Nombre"),
        title=models.CharField(max_length=200, verbose_name="Título profesional"),
        bio=models.TextField(verbose_name="Biografía"),
        location=models.CharField(max_length=100, verbose_name="Ubicación"),
        meta={'unique_together': [('language_code', 'name')]},
    )
    profile_image = models.ImageField(
        upload_to='profile/',
        verbose_name="Foto de perfil",
        help_text="Sube una imagen cuadrada (misma anchura y altura). Se optimizará automáticamente a 250x250px. Formatos: JPG, PNG, WebP. Máximo 3MB.",
        validators=[profile_image_validator, validate_no_executable],
    )
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    linkedin_url = models.URLField(blank=True, verbose_name="URL de LinkedIn")
    github_url = models.URLField(blank=True, verbose_name="URL de GitHub")
    medium_url = models.URLField(blank=True, verbose_name="URL de Medium")
    resume_pdf = models.FileField(
        upload_to='profile/',
        blank=True,
        verbose_name="CV en PDF (English)",
        help_text="Upload your resume in English (PDF format)",
        validators=[resume_pdf_validator, validate_no_executable],
    )
    resume_pdf_es = models.FileField(
        upload_to='profile/',
        blank=True,
        verbose_name="CV en PDF (Español)",
        help_text="Sube tu currículum en español (formato PDF)",
        validators=[resume_pdf_validator, validate_no_executable],
    )
    show_web_resume = models.BooleanField(default=True, verbose_name="Mostrar CV web")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or "Perfil"

    def save(self, *args, **kwargs):
        if not self.pk and Profile.objects.exists():
            raise ValidationError("Solo puede existir un perfil. Por favor edita el perfil existente.")

        if self.profile_image:
            optimize_uploaded_image(self.profile_image, image_type="profile", quality="high")

        return super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj = cls.objects.filter(pk=1).first()
        if not obj:
            default_language = getattr(settings, 'LANGUAGE_CODE', 'en')
            default_name = getattr(settings, 'PROFILE_NAME', 'Your Name')
            default_title = getattr(settings, 'PROFILE_TITLE', 'Your Title')
            default_location = getattr(settings, 'PROFILE_LOCATION', 'Your Location')
            default_email = getattr(settings, 'PROFILE_EMAIL', getattr(settings, 'DEFAULT_FROM_EMAIL', 'contact@example.com'))
            default_bio = getattr(settings, 'PROFILE_BIO', 'Update your biography to introduce yourself.')
            with transaction.atomic():
                # Use raw SQL to handle legacy columns (name, title, bio, location) in PostgreSQL
                from django.db import connection
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO portfolio_profile (id, email, phone, linkedin_url, github_url, medium_url, "
                    "profile_image, resume_pdf, resume_pdf_es, show_web_resume, created_at, updated_at, "
                    "name, title, bio, location) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s, %s, %s, %s)",
                    [1, default_email, '', '', '', '', '', '', '', True,
                     default_name, default_title, default_bio, default_location]
                )

                # Create translations for name, title, bio, location
                cursor.execute(
                    "INSERT INTO portfolio_profile_translation (master_id, language_code, name, title, bio, location) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    [1, default_language, default_name, default_title, default_bio, default_location]
                )

                # Fetch the created object
                obj = cls.objects.get(pk=1)

        else:
            default_language = getattr(settings, 'LANGUAGE_CODE', 'en')
            if not obj.safe_translation_getter('name', language_code=default_language, any_language=False):
                obj.set_current_language(default_language)
                obj.name = getattr(settings, 'PROFILE_NAME', 'Your Name')
                obj.title = getattr(settings, 'PROFILE_TITLE', 'Your Title')
                obj.bio = getattr(settings, 'PROFILE_BIO', 'Update your biography to introduce yourself.')
                obj.location = getattr(settings, 'PROFILE_LOCATION', 'Your Location')
                obj.save()
        return obj

    def delete(self, *args, **kwargs):
        raise ValidationError("No se puede eliminar el perfil. Solo puedes editarlo.")

    def get_resume_pdf_for_language(self, language_code):
        if language_code == "es" and self.resume_pdf_es:
            return self.resume_pdf_es
        if language_code == "en" and self.resume_pdf:
            return self.resume_pdf
        if self.resume_pdf_es:
            return self.resume_pdf_es
        if self.resume_pdf:
            return self.resume_pdf
        return None



class KnowledgeBase(TranslatableModel):
    """Modelo para bases de conocimiento (tecnologías, metodologías, áreas de experticia)"""

    # Clases CSS predeterminadas para bases de conocimiento comunes
    COMMON_KNOWLEDGE_ICONS = {
        # Lenguajes de programación
        'Python': 'fab fa-python',
        'JavaScript': 'fab fa-js-square',
        'Java': 'fab fa-java',
        'PHP': 'fab fa-php',
        'Swift': 'fab fa-swift',
        'Rust': 'fab fa-rust',
        'Go': 'fab fa-golang',
        'C++': 'fas fa-code',
        'C#': 'fas fa-code',
        'Ruby': 'fas fa-gem',
        'Kotlin': 'fab fa-android',
        'TypeScript': 'fab fa-js-square',
        
        # Frontend
        'React': 'fab fa-react',
        'Vue.js': 'fab fa-vuejs',
        'Angular': 'fab fa-angular',
        'HTML': 'fab fa-html5',
        'CSS': 'fab fa-css3-alt',
        'Sass': 'fab fa-sass',
        'Bootstrap': 'fab fa-bootstrap',
        'Tailwind CSS': 'fas fa-wind',
        
        # Backend/Frameworks
        'Django': 'fas fa-server',
        'Flask': 'fas fa-flask',
        'Node.js': 'fab fa-node-js',
        'Express.js': 'fas fa-server',
        'Laravel': 'fab fa-laravel',
        'Spring Boot': 'fas fa-leaf',
        'FastAPI': 'fas fa-rocket',
        
        # Bases de datos
        'PostgreSQL': 'fas fa-database',
        'MySQL': 'fas fa-database',
        'MongoDB': 'fas fa-database',
        'Redis': 'fas fa-database',
        'SQLite': 'fas fa-database',
        
        # DevOps/Cloud
        'Docker': 'fab fa-docker',
        'Kubernetes': 'fas fa-dharmachakra',
        'AWS': 'fab fa-aws',
        'Google Cloud': 'fab fa-google',
        'Azure': 'fab fa-microsoft',
        'Git': 'fab fa-git-alt',
        'GitHub': 'fab fa-github',
        'GitLab': 'fab fa-gitlab',
        
        # Herramientas
        'Linux': 'fab fa-linux',
        'Ubuntu': 'fab fa-ubuntu',
        'Windows': 'fab fa-windows',
        'macOS': 'fab fa-apple',
        'VS Code': 'fas fa-code',
        'Figma': 'fab fa-figma',
        'Slack': 'fab fa-slack',
        'Trello': 'fab fa-trello',
        
        # Mobile
        'Android': 'fab fa-android',
        'iOS': 'fab fa-apple',
        'React Native': 'fab fa-react',
        'Flutter': 'fas fa-mobile-alt',
        
        # Otros
        'WordPress': 'fab fa-wordpress',
        'Shopify': 'fab fa-shopify',
        'Firebase': 'fas fa-fire',
        'GraphQL': 'fas fa-project-diagram',
        'REST API': 'fas fa-exchange-alt',

        # Áreas de Conocimiento - Energía y Ingeniería
        'Battery Energy Storage': 'fas fa-battery-full',
        'Renewable Energy': 'fas fa-solar-panel',
        'AutoCAD': 'fas fa-drafting-compass',
        'Microgrid Planning': 'fas fa-plug',

        # Áreas de Conocimiento - Negocios y Gestión
        'Business Development': 'fas fa-chart-line',
        'Project Management': 'fas fa-tasks',
        'Innovation Management': 'fas fa-lightbulb',
        'Design Thinking': 'fas fa-lightbulb',
        'Sustainability Strategy': 'fas fa-leaf',
        'Agile': 'fas fa-sync-alt',

        # Áreas de Conocimiento - Tecnología y Datos
        'Data Analytics': 'fas fa-chart-line',
        'Machine Learning': 'fas fa-brain',
        'Edge Computing': 'fas fa-network-wired',
    }
    
    translations = TranslatedFields(
        name=models.CharField(max_length=50, verbose_name="Nombre")
    )
    identifier = models.CharField(
        max_length=60,
        unique=True,
        verbose_name="Identificador",
        help_text="Identificador estable (en ingles) utilizado como clave interna."
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Clase CSS del icono",
        help_text=(
            "Clase CSS para mostrar el icono. Ejemplos comunes:<br>"
            "- Python: <code>fab fa-python</code><br>"
            "- JavaScript: <code>fab fa-js-square</code><br>"
            "- React: <code>fab fa-react</code><br>"
            "- Docker: <code>fab fa-docker</code><br>"
            "- HTML: <code>fab fa-html5</code><br>"
            "- CSS: <code>fab fa-css3-alt</code><br>"
            "- Node.js: <code>fab fa-node-js</code><br>"
            "- Git: <code>fab fa-git-alt</code><br>"
            "- AWS: <code>fab fa-aws</code><br>"
            "- Linux: <code>fab fa-linux</code><br><br>"
            "<strong>Mas iconos disponibles en:</strong><br>"
            "<a href='https://fontawesome.com/icons' target='_blank'>Font Awesome Icons</a><br>"
            "<a href='https://devicon.dev/' target='_blank'>Devicon (iconos para desarrollo)</a><br>"
            "<a href='https://simpleicons.org/' target='_blank'>Simple Icons</a>"
        )
    )
    color = models.CharField(
        max_length=7,
        default='#000000',
        verbose_name="Color",
        help_text=(
            "Color en formato hexadecimal. Ejemplos de colores oficiales:<br>"
            "- Python: <code>#3776ab</code><br>"
            "- JavaScript: <code>#f7df1e</code><br>"
            "- React: <code>#61dafb</code><br>"
            "- Django: <code>#092e20</code><br>"
            "- Docker: <code>#2496ed</code><br>"
            "- Git: <code>#f05032</code><br>"
            "- AWS: <code>#ff9900</code><br>"
            "- PostgreSQL: <code>#336791</code>"
        )
    )
    class Meta:
        verbose_name = "Base de Conocimiento"
        verbose_name_plural = "Bases de Conocimiento"
        ordering = ['translations__name']

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or self.identifier or "Knowledge Base"

    def get_suggested_icon(self):
        """Retorna el icono sugerido para la base de conocimiento basado en el nombre"""
        key = self.identifier or self.safe_translation_getter('name', any_language=True)
        return self.COMMON_KNOWLEDGE_ICONS.get(key, 'fas fa-code')

    def get_suggested_color(self):
        """Retorna el color sugerido para la base de conocimiento basado en el nombre"""
        color_mapping = {
            'Python': '#3776ab',
            'JavaScript': '#f7df1e',
            'Java': '#ed8b00',
            'PHP': '#777bb4',
            'Swift': '#fa7343',
            'Rust': '#000000',
            'Go': '#00add8',
            'C++': '#00599c',
            'C#': '#239120',
            'Ruby': '#cc342d',
            'Kotlin': '#7f52ff',
            'TypeScript': '#3178c6',
            'React': '#61dafb',
            'Vue.js': '#4fc08d',
            'Angular': '#dd0031',
            'HTML': '#e34f26',
            'CSS': '#1572b6',
            'Sass': '#cc6699',
            'Bootstrap': '#7952b3',
            'Tailwind CSS': '#06b6d4',
            'Django': '#092e20',
            'Flask': '#000000',
            'Node.js': '#339933',
            'Express.js': '#000000',
            'Laravel': '#ff2d20',
            'Spring Boot': '#6db33f',
            'FastAPI': '#009688',
            'PostgreSQL': '#336791',
            'MySQL': '#4479a1',
            'MongoDB': '#47a248',
            'Redis': '#dc382d',
            'SQLite': '#003b57',
            'Docker': '#2496ed',
            'Kubernetes': '#326ce5',
            'AWS': '#ff9900',
            'Google Cloud': '#4285f4',
            'Azure': '#0078d4',
            'Git': '#f05032',
            'GitHub': '#181717',
            'GitLab': '#fc6d26',
            'Linux': '#fcc624',
            'Ubuntu': '#e95420',
            'Windows': '#0078d6',
            'macOS': '#000000',
            'VS Code': '#007acc',
            'Figma': '#f24e1e',
            'Slack': '#4a154b',
            'Trello': '#0079bf',
            'Android': '#3ddc84',
            'iOS': '#000000',
            'React Native': '#61dafb',
            'Flutter': '#02569b',
            'WordPress': '#21759b',
            'Shopify': '#7ab55c',
            'Firebase': '#ffca28',
            'GraphQL': '#e10098',
            'REST API': '#009688',

            # Áreas de Conocimiento - Energía y Ingeniería
            'BESS': '#28a745',
            'Battery Energy Storage': '#4CAF50',
            'Renewable Energy': '#8bc34a',
            'AutoCAD': '#e51937',
            'Microgrid Planning': '#4A90E2',

            # Áreas de Conocimiento - Negocios y Gestión
            'Business Development': '#0066cc',
            'Project Management': '#ff6b6b',
            'Innovation Management': '#ffd700',
            'Design Thinking': '#E67E22',
            'Sustainability Strategy': '#2ECC71',
            'Agile': '#009688',

            # Áreas de Conocimiento - Tecnología y Datos
            'Data Analytics': '#8E44AD',
            'Machine Learning': '#F39C12',
            'Edge Computing': '#2C3E50',
        }
        key = self.identifier or self.safe_translation_getter('name', any_language=True)
        return color_mapping.get(key, '#000000')


class ProjectType(TranslatableModel):
    """Modelo para tipos de proyectos"""

    translations = TranslatedFields(
        name=models.CharField(max_length=50, verbose_name="Nombre"),
        description=models.TextField(blank=True, verbose_name="Descripcion"),
    )
    slug = models.SlugField(unique=True, verbose_name="Slug")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tipo de Proyecto"
        verbose_name_plural = "Tipos de Proyectos"
        ordering = ['order', 'translations__name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_name = self.safe_translation_getter('name', any_language=True)
            if base_name:
                self.slug = slugify(base_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or self.slug or "Project Type"

    @property
    def project_count(self):
        """Retorna el número de proyectos de este tipo"""
        return self.project_set.filter(visibility='public').count()


class Project(TranslatableModel):
    """Modelo para proyectos del portafolio"""
    VISIBILITY_CHOICES = [
        ('public', 'Publico'),
        ('private', 'Privado'),
    ]

    PROJECT_TYPE_CHOICES = [
        ('framework', 'Framework'),
        ('tool', 'Tool'),
        ('website', 'Website'),
        ('template', 'Template'),
        ('dataset', 'Dataset'),
        ('mobile_app', 'Mobile App'),
        ('desktop_app', 'Desktop App'),
        ('library', 'Library'),
        ('api', 'API'),
        ('consulting', 'Consulting'),
        ('strategy', 'Strategy'),
        ('research', 'Research'),
        ('process', 'Process'),
        ('training', 'Training'),
        ('case_study', 'Case Study'),
        ('implementation', 'Implementation'),
        ('other', 'Other'),
    ]

    translations = TranslatedFields(
        title=models.CharField(max_length=200, verbose_name="Titulo"),
        description=models.TextField(verbose_name="Descripcion breve"),
        detailed_description=models.TextField(verbose_name="Descripcion detallada"),
    )
    slug = models.SlugField(unique=True, verbose_name="Slug",
                           help_text="URL amigable generada automaticamente")
    image = models.ImageField(
        upload_to='projects/',
        verbose_name="Imagen principal",
        blank=True,
        validators=[project_image_validator, validate_no_executable]
    )

    project_type_obj = models.ForeignKey(
        ProjectType,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Tipo de Proyecto",
        help_text="Tipo de proyecto principal"
    )

    project_type = models.CharField(
        max_length=20,
        choices=PROJECT_TYPE_CHOICES,
        default='other',
        blank=True,
        null=True,
        verbose_name="Tipo de proyecto",
        help_text="Categoria del proyecto (Framework, Tool, Website, etc.)"
    )
    stars_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Numero de estrellas",
        help_text="Para proyectos de GitHub, se actualiza automaticamente. Para proyectos privados, puedes agregar un numero estimado."
    )
    forks_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Numero de forks",
        help_text="Para proyectos de GitHub, se actualiza automaticamente"
    )
    primary_language = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Lenguaje principal",
        help_text="El lenguaje de programacion principal usado (Python, JavaScript, etc.)"
    )
    github_owner = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Propietario GitHub",
        help_text="Usuario/organizacion propietaria del repositorio (ej: microsoft, google)"
    )
    is_private_project = models.BooleanField(
        default=False,
        verbose_name="Proyecto privado/trabajo",
        help_text="Marcar si es un proyecto privado o de trabajo que no tiene repositorio publico"
    )

    knowledge_bases = models.ManyToManyField(KnowledgeBase, verbose_name="Bases de Conocimiento")
    github_url = models.URLField(blank=True, verbose_name="URL de GitHub")
    demo_url = models.URLField(blank=True, verbose_name="URL de demostracion")

    LINK_TYPE_CHOICES = [
        ('none', 'Sin enlace'),
        ('post', 'Enlace a Post'),
        ('github', 'Usar GitHub URL'),
        ('demo', 'Usar Demo URL'),
        ('pdf', 'Archivo PDF'),
        ('custom', 'URL personalizada'),
    ]

    featured_link_type = models.CharField(
        max_length=10,
        choices=LINK_TYPE_CHOICES,
        default='none',
        verbose_name="Tipo de enlace para Featured Work",
        help_text="Selecciona que tipo de enlace mostrar cuando el proyecto aparezca en Featured Work"
    )
    featured_link_post = models.ForeignKey(
        'BlogPost',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Post relacionado",
        help_text="Selecciona un post del blog para enlazar (solo si tipo es 'Enlace a Post')"
    )
    featured_link_pdf = models.FileField(
        upload_to='projects/pdfs/',
        blank=True,
        verbose_name="Archivo PDF",
        help_text="Sube un archivo PDF (solo si tipo es 'Archivo PDF')"
    )
    featured_link_custom = models.URLField(
        blank=True,
        verbose_name="URL personalizada",
        help_text="URL personalizada (solo si tipo es 'URL personalizada')"
    )

    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES,
                                 default='public', verbose_name="Visibilidad")
    featured = models.BooleanField(default=False, verbose_name="Proyecto destacado")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden de visualizacion")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.safe_translation_getter('title', any_language=True) or 'Proyecto'

    def get_absolute_url(self):
        return reverse('portfolio:project-detail', kwargs={'slug': self.slug})

    def get_primary_knowledge(self):
        """Retorna el conocimiento primario del proyecto"""
        from django.utils import translation

        current_language = translation.get_language() or settings.LANGUAGE_CODE
        knowledge_qs = self.knowledge_bases.language(current_language)

        if self.primary_language:
            kb = knowledge_qs.filter(
                models.Q(identifier__iexact=self.primary_language) |
                models.Q(translations__name__iexact=self.primary_language)
            ).first()
            if kb:
                return kb.safe_translation_getter('name', any_language=True)
            return self.primary_language

        kb = knowledge_qs.first()
        if kb:
            return kb.safe_translation_getter('name', any_language=True)
        return 'Code'

    def get_primary_knowledge_color(self):
        """Retorna el color del conocimiento primario"""
        from django.utils import translation

        current_language = translation.get_language() or settings.LANGUAGE_CODE
        knowledge_qs = self.knowledge_bases.language(current_language)

        kb = None
        if self.primary_language:
            kb = knowledge_qs.filter(
                models.Q(identifier__iexact=self.primary_language) |
                models.Q(translations__name__iexact=self.primary_language)
            ).first()

        if not kb:
            kb = knowledge_qs.first()

        if kb:
            return kb.color or kb.get_suggested_color()
        return '#6c757d'

    # Mantener métodos legacy para compatibilidad
    def get_primary_technology(self):
        """Legacy method - usa get_primary_knowledge()"""
        return self.get_primary_knowledge()

    def get_primary_technology_color(self):
        """Legacy method - usa get_primary_knowledge_color()"""
        return self.get_primary_knowledge_color()

    def get_github_display_url(self):
        if not self.github_url:
            return None
        try:
            from urllib.parse import urlparse
            path = urlparse(self.github_url).path.strip('/')
            if '/' in path:
                return path
        except Exception:
            pass
        return self.github_url

    def get_project_type_display_class(self):
        type_classes = {
            'framework': 'badge-framework',
            'tool': 'badge-tool',
            'website': 'badge-website',
            'template': 'badge-template',
            'dataset': 'badge-dataset',
            'mobile_app': 'badge-mobile',
            'desktop_app': 'badge-desktop',
            'library': 'badge-library',
            'api': 'badge-api',
            'other': 'badge-other',
        }
        return type_classes.get(self.project_type, 'badge-other')

    def get_featured_link_url(self):
        if self.featured_link_type == 'post' and self.featured_link_post:
            return self.featured_link_post.get_absolute_url()
        elif self.featured_link_type == 'github' and self.github_url:
            return self.github_url
        elif self.featured_link_type == 'demo' and self.demo_url:
            return self.demo_url
        elif self.featured_link_type == 'pdf' and self.featured_link_pdf:
            return self.featured_link_pdf.url
        elif self.featured_link_type == 'custom' and self.featured_link_custom:
            return self.featured_link_custom
        return None

    def get_featured_link_icon(self):
        icons = {
            'post': 'fas fa-arrow-right',
            'github': 'fab fa-github',
            'demo': 'fas fa-external-link-alt',
            'pdf': 'fas fa-file-pdf',
            'custom': 'fas fa-link',
        }
        return icons.get(self.featured_link_type, 'fas fa-link')

    def has_featured_link(self):
        return self.featured_link_type != 'none' and self.get_featured_link_url() is not None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        if self.image:
            optimize_uploaded_image(self.image, image_type='project', quality='medium')
            
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            # Handle duplicate slug error
            if "duplicate key value violates unique constraint" in str(e) and "portfolio_project_slug_key" in str(e):
                import uuid
                self.slug = f"{slugify(self.title)}-{uuid.uuid4().hex[:6]}"
                super().save(*args, **kwargs)
            else:
                raise e


class Experience(TranslatableModel):
    """Modelo para experiencia laboral"""

    translations = TranslatedFields(
        company=models.CharField(max_length=200, verbose_name="Empresa"),
        position=models.CharField(max_length=200, verbose_name="Posicion"),
        description=models.TextField(verbose_name="Descripcion del trabajo"),
    )
    start_date = models.DateField(verbose_name="Fecha de inicio")
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha de fin")
    current = models.BooleanField(default=False, verbose_name="Trabajo actual")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden de visualizacion")

    class Meta:
        verbose_name = "Experiencia"
        verbose_name_plural = "Experiencias"
        ordering = ['-start_date', 'order']

    def __str__(self):
        position = self.safe_translation_getter('position', any_language=True) or ''
        company = self.safe_translation_getter('company', any_language=True) or ''
        if position and company:
            return f"{position} en {company}"
        return position or company or "Experiencia"

    def save(self, *args, **kwargs):
        if self.current:
            self.end_date = None
        super().save(*args, **kwargs)


class Education(TranslatableModel):
    """Modelo para educacion y certificaciones"""
    EDUCATION_TYPES = [
        ('formal', 'Educacion Formal'),
        ('online_course', 'Curso Online'),
        ('certification', 'Certificacion'),
        ('bootcamp', 'Bootcamp'),
        ('workshop', 'Taller/Workshop'),
    ]

    translations = TranslatedFields(
        institution=models.CharField(max_length=200, verbose_name="Institucion"),
        degree=models.CharField(max_length=200, verbose_name="Titulo/Certificacion"),
        field_of_study=models.CharField(max_length=200, verbose_name="Campo de estudio"),
        description=models.TextField(blank=True, verbose_name="Descripcion"),
    )
    education_type = models.CharField(max_length=20, choices=EDUCATION_TYPES,
                                     default='formal', verbose_name="Tipo de educacion")
    start_date = models.DateField(verbose_name="Fecha de inicio")
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha de fin")
    current = models.BooleanField(default=False, verbose_name="En curso")
    credential_id = models.CharField(max_length=100, blank=True, verbose_name="ID del certificado")
    credential_url = models.URLField(blank=True, verbose_name="URL de verificacion")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden de visualizacion")

    class Meta:
        verbose_name = "Educacion"
        verbose_name_plural = "Educacion"
        ordering = ['-end_date', '-start_date']

    def __str__(self):
        degree = self.safe_translation_getter('degree', any_language=True) or ''
        institution = self.safe_translation_getter('institution', any_language=True) or ''
        if degree and institution:
            return f"{degree} - {institution}"
        return degree or institution or "Educacion"

    def save(self, *args, **kwargs):
        if self.current:
            self.end_date = None
        super().save(*args, **kwargs)


class Skill(TranslatableModel):
    """Modelo para habilidades tecnicas"""
    PROFICIENCY_CHOICES = [
        (1, 'Basico'),
        (2, 'Intermedio'),
        (3, 'Avanzado'),
        (4, 'Experto'),
    ]

    translations = TranslatedFields(
        name=models.CharField(max_length=100, verbose_name="Nombre de la habilidad"),
    )
    proficiency = models.IntegerField(choices=PROFICIENCY_CHOICES, verbose_name="Nivel de competencia")
    years_experience = models.PositiveIntegerField(verbose_name="Anios de experiencia")
    category = models.CharField(max_length=100, verbose_name="Categoria",
                               help_text="Ej: Programming, Cloud, Business, Methodologies, etc.")

    @property
    def proficiency_label(self):
        """Return a human-friendly proficiency label in the active language."""
        from django.utils import translation

        language = (translation.get_language() or settings.LANGUAGE_CODE or "en")[:2]
        localized_labels = {
            "en": {
                1: "Beginner",
                2: "Intermediate",
                3: "Advanced",
                4: "Expert",
            },
            "es": {
                1: "Basico",
                2: "Intermedio",
                3: "Avanzado",
                4: "Experto",
            },
        }
        return localized_labels.get(language, {}).get(
            self.proficiency, self.get_proficiency_display()
        )

    class Meta:
        verbose_name = "Habilidad"
        verbose_name_plural = "Habilidades"
        ordering = ['category', '-proficiency', 'translations__name']

    def __str__(self):
        name = self.safe_translation_getter('name', any_language=True) or 'Habilidad'
        return f"{name} ({self.get_proficiency_display()})"

    def proficiency_bar(self):
        return min(max((self.proficiency / 4) * 100, 0), 100)


class Language(TranslatableModel):
    """Modelo para idiomas y nivel de dominio"""

    PROFICIENCY_LEVELS = [
        ('A1', 'A1 - Beginner'),
        ('A2', 'A2 - Elementary'),
        ('B1', 'B1 - Intermediate'),
        ('B2', 'B2 - Upper Intermediate'),
        ('C1', 'C1 - Advanced'),
        ('C2', 'C2 - Proficient'),
        ('Native', 'Native'),
    ]

    translations = TranslatedFields(
        name=models.CharField(
            max_length=50,
            verbose_name="Idioma",
            help_text="Ej: English, Espanol, Francais"
        )
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Codigo",
        help_text="Identificador interno del idioma (en, es, fr, etc.)"
    )
    proficiency = models.CharField(
        max_length=10,
        choices=PROFICIENCY_LEVELS,
        verbose_name="Nivel de dominio"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden de visualizacion",
        help_text="Orden en que aparecera en el CV"
    )

    class Meta:
        verbose_name = "Idioma"
        verbose_name_plural = "Idiomas"
        ordering = ['order', 'translations__name']

    def __str__(self):
        name = self.safe_translation_getter('name', any_language=True) or self.code
        return f"{name} ({self.proficiency})"


class Category(TranslatableModel):
    """Modelo para categorias del blog"""

    translations = TranslatedFields(
        name=models.CharField(max_length=100, verbose_name="Nombre"),
        description=models.TextField(blank=True, verbose_name="Descripcion"),
    )
    slug = models.SlugField(unique=True, verbose_name="Slug")
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['order', 'translations__name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_name = self.safe_translation_getter('name', any_language=True)
            if base_name:
                self.slug = slugify(base_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or "Categoria"

    @property
    def post_count(self):
        return self.blogpost_set.filter(status='published').count()


class BlogPost(TranslatableModel):
    """Modelo para posts del blog/noticias"""
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
        ('archived', 'Archivado'),
    ]

    translations = TranslatedFields(
        title=models.CharField(max_length=200, verbose_name="Titulo"),
        content=models.TextField(verbose_name="Contenido"),
        excerpt=models.TextField(max_length=300, verbose_name="Extracto"),
    )
    slug = models.SlugField(unique=True, verbose_name="Slug")
    featured_image = models.ImageField(
        upload_to='blog/',
        blank=True,
        verbose_name="Imagen destacada",
        validators=[blog_image_validator, validate_no_executable]
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Categoria",
        help_text="Categoria principal del post"
    )

    tags = models.CharField(max_length=200, blank=True, verbose_name="Tags",
                           help_text="Tags separados por comas")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name="Estado")
    publish_date = models.DateTimeField(verbose_name="Fecha de publicacion")
    reading_time = models.PositiveIntegerField(default=5, verbose_name="Tiempo de lectura (minutos)")
    featured = models.BooleanField(default=False, verbose_name="Post destacado")

    github_url = models.URLField(blank=True, verbose_name="URL de GitHub",
                               help_text="Repositorio relacionado con el post")
    medium_url = models.URLField(blank=True, verbose_name="URL de Medium",
                               help_text="Enlace al articulo en Medium")
    linkedin_url = models.URLField(blank=True, verbose_name="URL de LinkedIn",
                                 help_text="Enlace al post en LinkedIn")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Post del Blog"
        verbose_name_plural = "Posts del Blog"
        ordering = ['-publish_date']

    def __str__(self):
        return self.safe_translation_getter('title', any_language=True) or 'Post'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.featured_image:
            optimize_uploaded_image(self.featured_image, image_type='blog', quality='medium')
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('portfolio:post-detail', kwargs={'slug': self.slug})

    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []

    def get_post_type_display(self):
        if self.category:
            return self.category.name
        return "Sin categoria"

    def get_category_color(self):
        if hasattr(self, 'category') and self.category:
            return self.category.color
        return "#6c757d"

    def get_category_icon(self):
        if hasattr(self, 'category') and self.category:
            return self.category.icon
        return "fas fa-newspaper"


class Contact(models.Model):
    """Modelo para mensajes de contacto"""
    name = models.CharField(max_length=100, verbose_name="Nombre")
    email = models.EmailField(verbose_name="Email")
    subject = models.CharField(max_length=200, verbose_name="Asunto")
    message = models.TextField(verbose_name="Mensaje")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de envío")
    read = models.BooleanField(default=False, verbose_name="Leído")

    class Meta:
        verbose_name = "Mensaje de Contacto"
        verbose_name_plural = "Mensajes de Contacto"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


class PageVisit(models.Model):
    """Modelo para tracking básico de visitas"""
    page_url = models.CharField(max_length=500, verbose_name="URL de la página")
    page_title = models.CharField(max_length=200, verbose_name="Título de la página")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora")
    ip_address = models.GenericIPAddressField(verbose_name="Dirección IP")
    user_agent = models.TextField(verbose_name="User Agent")

    class Meta:
        verbose_name = "Visita de Página"
        verbose_name_plural = "Visitas de Páginas"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.page_url} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
