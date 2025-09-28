from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from .validators import (
    profile_image_validator, 
    project_image_validator, 
    blog_image_validator, 
    resume_pdf_validator,
    validate_no_executable,
    validate_filename
)


class Profile(models.Model):
    """Modelo para información personal del portafolio"""
    name = models.CharField(max_length=100, verbose_name="Nombre")
    title = models.CharField(max_length=200, verbose_name="Título profesional")
    bio = models.TextField(verbose_name="Biografía")
    profile_image = models.ImageField(
        upload_to='profile/', 
        verbose_name="Foto de perfil",
        validators=[profile_image_validator, validate_no_executable]
    )
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    location = models.CharField(max_length=100, verbose_name="Ubicación")
    linkedin_url = models.URLField(blank=True, verbose_name="URL de LinkedIn")
    github_url = models.URLField(blank=True, verbose_name="URL de GitHub")
    medium_url = models.URLField(blank=True, verbose_name="URL de Medium")
    resume_pdf = models.FileField(
        upload_to='profile/', 
        blank=True, 
        verbose_name="CV en PDF",
        validators=[resume_pdf_validator, validate_no_executable]
    )
    show_web_resume = models.BooleanField(default=True, verbose_name="Mostrar CV web")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return self.name


class Technology(models.Model):
    """Modelo para tecnologías utilizadas en proyectos"""
    
    # Clases CSS predeterminadas para tecnologías comunes
    COMMON_TECH_ICONS = {
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
    }
    
    name = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    icon = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name="Clase CSS del icono",
        help_text=(
            "Clase CSS para mostrar el icono. Ejemplos comunes:<br>"
            "• Python: <code>fab fa-python</code><br>"
            "• JavaScript: <code>fab fa-js-square</code><br>"
            "• React: <code>fab fa-react</code><br>"
            "• Docker: <code>fab fa-docker</code><br>"
            "• HTML: <code>fab fa-html5</code><br>"
            "• CSS: <code>fab fa-css3-alt</code><br>"
            "• Node.js: <code>fab fa-node-js</code><br>"
            "• Git: <code>fab fa-git-alt</code><br>"
            "• AWS: <code>fab fa-aws</code><br>"
            "• Linux: <code>fab fa-linux</code><br><br>"
            "📚 <strong>Más iconos disponibles en:</strong><br>"
            "🔗 <a href='https://fontawesome.com/icons' target='_blank'>Font Awesome Icons</a><br>"
            "🔗 <a href='https://devicon.dev/' target='_blank'>Devicon (Iconos específicos para desarrollo)</a><br>"
            "🔗 <a href='https://simpleicons.org/' target='_blank'>Simple Icons</a>"
        )
    )
    color = models.CharField(
        max_length=7, 
        default='#000000', 
        verbose_name="Color", 
        help_text=(
            "Color en formato hexadecimal. Ejemplos de colores oficiales:<br>"
            "• Python: <code>#3776ab</code><br>"
            "• JavaScript: <code>#f7df1e</code><br>"
            "• React: <code>#61dafb</code><br>"
            "• Django: <code>#092e20</code><br>"
            "• Docker: <code>#2496ed</code><br>"
            "• Git: <code>#f05032</code><br>"
            "• AWS: <code>#ff9900</code><br>"
            "• PostgreSQL: <code>#336791</code>"
        )
    )

    class Meta:
        verbose_name = "Tecnología"
        verbose_name_plural = "Tecnologías"
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_suggested_icon(self):
        """Retorna el icono sugerido para la tecnología basado en el nombre"""
        return self.COMMON_TECH_ICONS.get(self.name, 'fas fa-code')
    
    def get_suggested_color(self):
        """Retorna el color sugerido para la tecnología basado en el nombre"""
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
        }
        return color_mapping.get(self.name, '#000000')


class ProjectType(models.Model):
    """Modelo para tipos de proyectos"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tipo de Proyecto"
        verbose_name_plural = "Tipos de Proyectos"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def project_count(self):
        """Retorna el número de proyectos de este tipo"""
        return self.project_set.filter(visibility='public').count()


class Project(models.Model):
    """Modelo para proyectos del portafolio"""
    VISIBILITY_CHOICES = [
        ('public', 'Público'),
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

    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(unique=True, verbose_name="Slug",
                           help_text="URL amigable generada automáticamente")
    description = models.TextField(verbose_name="Descripción breve")
    detailed_description = models.TextField(verbose_name="Descripción detallada")
    image = models.ImageField(
        upload_to='projects/', 
        verbose_name="Imagen principal", 
        blank=True,
        validators=[project_image_validator, validate_no_executable]
    )

    # Nueva relación con tipos de proyectos (reemplaza project_type)
    project_type_obj = models.ForeignKey(
        ProjectType,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Tipo de Proyecto",
        help_text="Tipo de proyecto principal"
    )

    # Mantener project_type temporalmente para migración
    project_type = models.CharField(
        max_length=20,
        choices=PROJECT_TYPE_CHOICES,
        default='other',
        blank=True,
        null=True,
        verbose_name="Tipo de proyecto",
        help_text="Categoría del proyecto (Framework, Tool, Website, etc.)"
    )
    stars_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Número de estrellas",
        help_text="Para proyectos de GitHub, se actualiza automáticamente. Para proyectos privados, puedes agregar un número estimado."
    )
    forks_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Número de forks",
        help_text="Para proyectos de GitHub, se actualiza automáticamente"
    )
    primary_language = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Lenguaje principal",
        help_text="El lenguaje de programación principal usado (Python, JavaScript, etc.)"
    )
    github_owner = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Propietario GitHub",
        help_text="Usuario/organización propietaria del repositorio (ej: microsoft, google)"
    )
    is_private_project = models.BooleanField(
        default=False,
        verbose_name="Proyecto privado/trabajo",
        help_text="Marcar si es un proyecto privado o de trabajo que no tiene repositorio público"
    )

    technologies = models.ManyToManyField(Technology, verbose_name="Tecnologías utilizadas")
    github_url = models.URLField(blank=True, verbose_name="URL de GitHub")
    demo_url = models.URLField(blank=True, verbose_name="URL de demostración")

    # Featured work link options
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
        help_text="Selecciona qué tipo de enlace mostrar cuando el proyecto aparezca en Featured Work"
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
    order = models.PositiveIntegerField(default=0, verbose_name="Orden de visualización")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('portfolio:project-detail', kwargs={'slug': self.slug})

    def get_primary_technology(self):
        """Retorna la primera tecnología para mostrar como lenguaje principal"""
        if self.primary_language:
            return self.primary_language
        tech = self.technologies.first()
        return tech.name if tech else 'Code'

    def get_primary_technology_color(self):
        """Retorna el color de la tecnología principal"""
        if self.primary_language:
            # Buscar por nombre del lenguaje principal
            tech = self.technologies.filter(name__iexact=self.primary_language).first()
            if tech:
                return tech.color
        # Si no, usar la primera tecnología
        tech = self.technologies.first()
        return tech.color if tech else '#6c757d'

    def get_github_display_url(self):
        """Retorna el texto para mostrar del GitHub (owner/repo)"""
        if not self.github_url:
            return None
        try:
            # Extraer owner/repo de la URL de GitHub
            from urllib.parse import urlparse
            path = urlparse(self.github_url).path.strip('/')
            if '/' in path:
                return path
        except:
            pass
        return self.github_url

    def get_project_type_display_class(self):
        """Retorna la clase CSS para el tipo de proyecto"""
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
        """Retorna la URL para featured work basada en el tipo seleccionado"""
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
        """Retorna el icono para el enlace de featured work"""
        icons = {
            'post': 'fas fa-arrow-right',
            'github': 'fab fa-github',
            'demo': 'fas fa-external-link-alt',
            'pdf': 'fas fa-file-pdf',
            'custom': 'fas fa-link',
        }
        return icons.get(self.featured_link_type, 'fas fa-link')

    def has_featured_link(self):
        """Verifica si el proyecto tiene un enlace configurado para featured work"""
        return self.featured_link_type != 'none' and self.get_featured_link_url() is not None


class Experience(models.Model):
    """Modelo para experiencia laboral"""
    company = models.CharField(max_length=200, verbose_name="Empresa")
    position = models.CharField(max_length=200, verbose_name="Posición")
    description = models.TextField(verbose_name="Descripción del trabajo")
    start_date = models.DateField(verbose_name="Fecha de inicio")
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha de fin")
    current = models.BooleanField(default=False, verbose_name="Trabajo actual")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden de visualización")

    class Meta:
        verbose_name = "Experiencia"
        verbose_name_plural = "Experiencias"
        ordering = ['-start_date', 'order']

    def __str__(self):
        return f"{self.position} en {self.company}"

    def save(self, *args, **kwargs):
        # Si es trabajo actual, limpiar end_date
        if self.current:
            self.end_date = None
        super().save(*args, **kwargs)


class Education(models.Model):
    """Modelo para educación y certificaciones"""
    EDUCATION_TYPES = [
        ('formal', 'Educación Formal'),           # Universidad, instituto
        ('online_course', 'Curso Online'),        # Coursera, Platzi, Udemy
        ('certification', 'Certificación'),       # AWS, Google, Microsoft
        ('bootcamp', 'Bootcamp'),                 # Coding bootcamps
        ('workshop', 'Taller/Workshop'),          # Eventos cortos
    ]
    
    institution = models.CharField(max_length=200, verbose_name="Institución")
    degree = models.CharField(max_length=200, verbose_name="Título/Certificación")
    field_of_study = models.CharField(max_length=200, verbose_name="Campo de estudio")
    education_type = models.CharField(max_length=20, choices=EDUCATION_TYPES, 
                                     default='formal', verbose_name="Tipo de educación")
    start_date = models.DateField(verbose_name="Fecha de inicio")
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha de fin")
    current = models.BooleanField(default=False, verbose_name="En curso")
    description = models.TextField(blank=True, verbose_name="Descripción")
    credential_id = models.CharField(max_length=100, blank=True, verbose_name="ID del certificado")
    credential_url = models.URLField(blank=True, verbose_name="URL de verificación")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden de visualización")
    
    class Meta:
        verbose_name = "Educación"
        verbose_name_plural = "Educación"
        ordering = ['-end_date', '-start_date']

    def __str__(self):
        return f"{self.degree} - {self.institution}"

    def save(self, *args, **kwargs):
        # Si está en curso, limpiar end_date
        if self.current:
            self.end_date = None
        super().save(*args, **kwargs)


class Skill(models.Model):
    """Modelo para habilidades técnicas"""
    PROFICIENCY_CHOICES = [
        (1, 'Básico'),
        (2, 'Intermedio'),
        (3, 'Avanzado'),
        (4, 'Experto'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nombre de la habilidad")
    proficiency = models.IntegerField(choices=PROFICIENCY_CHOICES, verbose_name="Nivel de competencia")
    years_experience = models.PositiveIntegerField(verbose_name="Años de experiencia")
    category = models.CharField(max_length=100, verbose_name="Categoría", 
                               help_text="Ej: Programming, Cloud, Business, Methodologies, etc.")

    class Meta:
        verbose_name = "Habilidad"
        verbose_name_plural = "Habilidades"
        ordering = ['category', '-proficiency', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_proficiency_display()})"

    def get_proficiency_percentage(self):
        """Retorna el nivel de competencia como porcentaje para barras de progreso"""
        return (self.proficiency / 4) * 100


class Category(models.Model):
    """Modelo para categorías de posts del blog"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def post_count(self):
        """Retorna el número de posts publicados en esta categoría"""
        return self.blogpost_set.filter(status='published').count()


class BlogPost(models.Model):
    """Modelo para posts del blog/noticias"""
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
        ('archived', 'Archivado'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    content = models.TextField(verbose_name="Contenido")
    excerpt = models.TextField(max_length=300, verbose_name="Extracto")
    featured_image = models.ImageField(
        upload_to='blog/', 
        blank=True, 
        verbose_name="Imagen destacada",
        validators=[blog_image_validator, validate_no_executable]
    )
    # Nueva relación con categorías (reemplaza post_type)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Categoría",
        help_text="Categoría principal del post"
    )

    tags = models.CharField(max_length=200, blank=True, verbose_name="Tags", 
                           help_text="Tags separados por comas")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name="Estado")
    publish_date = models.DateTimeField(verbose_name="Fecha de publicación")
    reading_time = models.PositiveIntegerField(default=5, verbose_name="Tiempo de lectura (minutos)")
    featured = models.BooleanField(default=False, verbose_name="Post destacado")

    # Reference links
    github_url = models.URLField(blank=True, verbose_name="URL de GitHub",
                               help_text="Repositorio relacionado con el post")
    medium_url = models.URLField(blank=True, verbose_name="URL de Medium",
                               help_text="Enlace al artículo en Medium")
    linkedin_url = models.URLField(blank=True, verbose_name="URL de LinkedIn",
                                 help_text="Enlace al post en LinkedIn")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Post del Blog"
        verbose_name_plural = "Posts del Blog"
        ordering = ['-publish_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('portfolio:post-detail', kwargs={'slug': self.slug})

    def get_tags_list(self):
        """Retorna los tags como lista"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []

    def get_post_type_display(self):
        """Retorna el nombre de la categoría (compatibilidad hacia atrás)"""
        if self.category:
            return self.category.name
        return "Sin categoría"

    def get_category_color(self):
        """Retorna el color de la categoría"""
        if hasattr(self, 'category') and self.category:
            return self.category.color
        return "#6c757d"  # Color por defecto

    def get_category_icon(self):
        """Retorna el icono de la categoría"""
        if hasattr(self, 'category') and self.category:
            return self.category.icon
        return "fas fa-newspaper"  # Icono por defecto


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