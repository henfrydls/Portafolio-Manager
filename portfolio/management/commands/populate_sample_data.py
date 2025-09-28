"""
Management command to populate the portfolio with comprehensive sample data.
This creates a complete portfolio example that showcases all features.
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from portfolio.models import (
    Profile, Project, Technology, Experience, Education, Skill,
    BlogPost, Contact, Category, ProjectType
)
import random


class Command(BaseCommand):
    help = 'Populate the portfolio with comprehensive sample data for demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all data before populating (WARNING: This will delete existing data)',
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default='admin123',
            help='Password for the sample admin user (default: admin123)',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(
                self.style.WARNING('⚠️  Resetting all data... This will delete existing content!')
            )
            self.reset_data()

        self.stdout.write('🚀 Creating comprehensive sample data...')

        # Create admin user
        admin_password = options['admin_password']
        admin_user = self.create_admin_user(admin_password)

        # Create categories first
        categories = self.create_categories()

        # Create project types
        project_types = self.create_project_types()

        # Create technologies (if not exist)
        self.create_technologies()

        # Create profile
        profile = self.create_profile()

        # Create experience
        experiences = self.create_experiences()

        # Create education
        educations = self.create_educations()

        # Create skills
        skills = self.create_skills()

        # Create projects
        projects = self.create_projects(project_types)

        # Create blog posts
        blog_posts = self.create_blog_posts(categories)

        # Create sample contacts
        contacts = self.create_sample_contacts()

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Sample data created successfully!\n'
                f'📊 Summary:\n'
                f'   • Admin User: admin (password: {admin_password})\n'
                f'   • Profile: 1 complete profile\n'
                f'   • Experience: {len(experiences)} job positions\n'
                f'   • Education: {len(educations)} education entries\n'
                f'   • Skills: {len(skills)} technical skills\n'
                f'   • Projects: {len(projects)} portfolio projects\n'
                f'   • Blog Posts: {len(blog_posts)} articles\n'
                f'   • Categories: {len(categories)} blog categories\n'
                f'   • Contacts: {len(contacts)} sample messages\n'
                f'   • Technologies: Auto-populated with icons\n\n'
                f'🌐 Access URLs:\n'
                f'   • Portfolio: http://localhost:8000/\n'
                f'   • Admin: http://localhost:8000/admin/ (admin/{admin_password})\n'
                f'   • Dashboard: http://localhost:8000/admin-dashboard/\n'
                f'   • Analytics: http://localhost:8000/admin-analytics/\n'
            )
        )

    def reset_data(self):
        """Reset all portfolio data"""
        models_to_reset = [Contact, BlogPost, Project, Experience, Education, Skill, Profile]

        for model in models_to_reset:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(f'   Deleted {count} {model.__name__} records')

    def create_admin_user(self, password):
        """Create admin user if it doesn't exist"""
        if User.objects.filter(username='admin').exists():
            admin_user = User.objects.get(username='admin')
            self.stdout.write('👤 Admin user already exists')
        else:
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@portfolio.com',
                password=password,
                first_name='Portfolio',
                last_name='Admin'
            )
            self.stdout.write(self.style.SUCCESS(f'👤 Created admin user (password: {password})'))

        return admin_user

    def create_categories(self):
        """Create blog categories"""
        categories_data = [
            {'name': 'Desarrollo Web', 'slug': 'desarrollo-web', 'description': 'Artículos sobre desarrollo web frontend y backend', 'order': 1},
            {'name': 'Inteligencia Artificial', 'slug': 'inteligencia-artificial', 'description': 'Contenido sobre IA, ML y Data Science', 'order': 2},
            {'name': 'DevOps', 'slug': 'devops', 'description': 'Herramientas y prácticas de DevOps', 'order': 3},
            {'name': 'Tutorial', 'slug': 'tutorial', 'description': 'Guías paso a paso y tutoriales', 'order': 4},
            {'name': 'Opinión', 'slug': 'opinion', 'description': 'Reflexiones y opiniones técnicas', 'order': 5},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories.append(category)
            if created:
                self.stdout.write(f'   📁 Created category: {category.name}')

        return categories

    def create_project_types(self):
        """Create project types"""
        types_data = [
            {'name': 'Aplicación Web', 'slug': 'web-app', 'order': 1},
            {'name': 'API REST', 'slug': 'api-rest', 'order': 2},
            {'name': 'Aplicación Móvil', 'slug': 'mobile-app', 'order': 3},
            {'name': 'Dashboard', 'slug': 'dashboard', 'order': 4},
            {'name': 'E-commerce', 'slug': 'ecommerce', 'order': 5},
            {'name': 'Automatización', 'slug': 'automation', 'order': 6},
        ]

        project_types = []
        for type_data in types_data:
            project_type, created = ProjectType.objects.get_or_create(
                slug=type_data['slug'],
                defaults=type_data
            )
            project_types.append(project_type)
            if created:
                self.stdout.write(f'   🏷️ Created project type: {project_type.name}')

        return project_types

    def create_technologies(self):
        """Create sample technologies if they don't exist"""
        # This assumes the populate_technologies command exists
        from django.core.management import call_command
        try:
            call_command('populate_technologies')
            self.stdout.write('⚡ Technologies populated automatically')
        except CommandError:
            self.stdout.write(self.style.WARNING('⚠️  Could not auto-populate technologies'))

    def create_profile(self):
        """Create sample profile"""
        if Profile.objects.exists():
            profile = Profile.objects.first()
            self.stdout.write('👤 Profile already exists, updating...')
        else:
            profile = Profile.objects.create()
            self.stdout.write('👤 Created new profile')

        # Update profile with sample data
        profile.name = "Alex Developer"
        profile.professional_title = "Full Stack Developer & Tech Lead"
        profile.bio = """Desarrollador Full Stack apasionado por crear soluciones tecnológicas innovadoras.
        Con más de 5 años de experiencia en desarrollo web, especializado en Python/Django, React y arquitecturas cloud.

        Me encanta resolver problemas complejos y colaborar en equipos multidisciplinarios para entregar productos de calidad.
        Cuando no estoy programando, disfruto contribuir a proyectos open source y escribir sobre tecnología."""

        profile.email = "alex@portfolio.com"
        profile.phone = "+1 (555) 123-4567"
        profile.location = "San Francisco, CA"
        profile.linkedin_url = "https://linkedin.com/in/alex-developer"
        profile.github_url = "https://github.com/alex-developer"
        profile.medium_url = "https://medium.com/@alex-developer"
        profile.website_url = "https://alexdev.portfolio.com"
        profile.save()

        return profile

    def create_experiences(self):
        """Create sample work experiences"""
        experiences_data = [
            {
                'job_title': 'Senior Full Stack Developer',
                'company': 'TechCorp Solutions',
                'location': 'San Francisco, CA',
                'start_date': datetime(2022, 3, 1).date(),
                'end_date': None,
                'current': True,
                'description': """• Lidero un equipo de 4 desarrolladores en la creación de aplicaciones web escalables
• Implementé arquitectura microservicios que redujo los tiempos de respuesta en 40%
• Desarrollé APIs REST con Django y frontend con React, sirviendo a +10k usuarios diarios
• Implementé CI/CD con Docker y AWS, automatizando deployments y reduciendo errores en 60%""",
                'order': 1
            },
            {
                'job_title': 'Full Stack Developer',
                'company': 'StartupXYZ',
                'location': 'Remote',
                'start_date': datetime(2020, 6, 1).date(),
                'end_date': datetime(2022, 2, 28).date(),
                'current': False,
                'description': """• Desarrollé desde cero una plataforma de e-commerce que generó $500k en su primer año
• Creé sistema de pagos integrado con Stripe y PayPal, procesando +1000 transacciones mensuales
• Optimicé la base de datos PostgreSQL mejorando queries en 70%
• Implementé sistema de notificaciones en tiempo real con WebSockets""",
                'order': 2
            },
            {
                'job_title': 'Backend Developer',
                'company': 'Digital Agency Pro',
                'location': 'New York, NY',
                'start_date': datetime(2019, 1, 15).date(),
                'end_date': datetime(2020, 5, 30).date(),
                'current': False,
                'description': """• Desarrollé APIs para aplicaciones móviles con Django REST Framework
• Integré servicios de terceros (AWS S3, SendGrid, Google Maps API)
• Implementé sistema de autenticación JWT y manejo de roles
• Mantuve 99.8% uptime en aplicaciones críticas de clientes""",
                'order': 3
            },
            {
                'job_title': 'Junior Web Developer',
                'company': 'WebStudio Creative',
                'location': 'Los Angeles, CA',
                'start_date': datetime(2018, 8, 1).date(),
                'end_date': datetime(2018, 12, 31).date(),
                'current': False,
                'description': """• Desarrollé sitios web responsivos con HTML5, CSS3 y JavaScript
• Colaboré en proyectos WordPress para pequeñas y medianas empresas
• Aprendí fundamentos de desarrollo backend con PHP y MySQL
• Participé en más de 15 proyectos web exitosos""",
                'order': 4
            }
        ]

        experiences = []
        for exp_data in experiences_data:
            experience, created = Experience.objects.get_or_create(
                job_title=exp_data['job_title'],
                company=exp_data['company'],
                defaults=exp_data
            )
            experiences.append(experience)
            if created:
                self.stdout.write(f'   💼 Created experience: {experience.job_title} at {experience.company}')

        return experiences

    def create_educations(self):
        """Create sample education entries"""
        educations_data = [
            {
                'degree': 'Computer Science, B.S.',
                'institution': 'Stanford University',
                'location': 'Stanford, CA',
                'start_date': datetime(2014, 9, 1).date(),
                'end_date': datetime(2018, 6, 15).date(),
                'current': False,
                'description': """Licenciatura en Ciencias de la Computación con concentración en Ingeniería de Software.

Cursos relevantes: Algoritmos y Estructuras de Datos, Bases de Datos, Ingeniería de Software,
Sistemas Distribuidos, Machine Learning, Desarrollo Web.""",
                'order': 1
            },
            {
                'degree': 'AWS Solutions Architect Professional',
                'institution': 'Amazon Web Services',
                'location': 'Online',
                'start_date': datetime(2023, 1, 1).date(),
                'end_date': datetime(2023, 3, 15).date(),
                'current': False,
                'description': """Certificación profesional en arquitectura de soluciones cloud con AWS.

Competencias: EC2, RDS, Lambda, API Gateway, CloudFormation, VPC, Security Groups,
Diseño de arquitecturas escalables y fault-tolerant.""",
                'order': 2
            },
            {
                'degree': 'Full Stack Web Development Bootcamp',
                'institution': 'General Assembly',
                'location': 'San Francisco, CA',
                'start_date': datetime(2018, 3, 1).date(),
                'end_date': datetime(2018, 6, 1).date(),
                'current': False,
                'description': """Bootcamp intensivo de 12 semanas enfocado en desarrollo web full stack.

Tecnologías: HTML5, CSS3, JavaScript, React, Node.js, Express, MongoDB, PostgreSQL, Git.""",
                'order': 3
            }
        ]

        educations = []
        for edu_data in educations_data:
            education, created = Education.objects.get_or_create(
                degree=edu_data['degree'],
                institution=edu_data['institution'],
                defaults=edu_data
            )
            educations.append(education)
            if created:
                self.stdout.write(f'   🎓 Created education: {education.degree} from {education.institution}')

        return educations

    def create_skills(self):
        """Create sample skills"""
        skills_data = [
            # Programming Languages
            {'name': 'Python', 'proficiency': 'expert', 'years_experience': 5, 'category': 'languages', 'order': 1},
            {'name': 'JavaScript', 'proficiency': 'expert', 'years_experience': 4, 'category': 'languages', 'order': 2},
            {'name': 'TypeScript', 'proficiency': 'advanced', 'years_experience': 2, 'category': 'languages', 'order': 3},
            {'name': 'Java', 'proficiency': 'intermediate', 'years_experience': 2, 'category': 'languages', 'order': 4},

            # Frontend
            {'name': 'React', 'proficiency': 'expert', 'years_experience': 4, 'category': 'frontend', 'order': 5},
            {'name': 'Vue.js', 'proficiency': 'advanced', 'years_experience': 2, 'category': 'frontend', 'order': 6},
            {'name': 'HTML5', 'proficiency': 'expert', 'years_experience': 5, 'category': 'frontend', 'order': 7},
            {'name': 'CSS3', 'proficiency': 'expert', 'years_experience': 5, 'category': 'frontend', 'order': 8},
            {'name': 'Sass', 'proficiency': 'advanced', 'years_experience': 3, 'category': 'frontend', 'order': 9},

            # Backend
            {'name': 'Django', 'proficiency': 'expert', 'years_experience': 5, 'category': 'backend', 'order': 10},
            {'name': 'FastAPI', 'proficiency': 'advanced', 'years_experience': 2, 'category': 'backend', 'order': 11},
            {'name': 'Node.js', 'proficiency': 'advanced', 'years_experience': 3, 'category': 'backend', 'order': 12},
            {'name': 'Flask', 'proficiency': 'intermediate', 'years_experience': 2, 'category': 'backend', 'order': 13},

            # Databases
            {'name': 'PostgreSQL', 'proficiency': 'expert', 'years_experience': 4, 'category': 'databases', 'order': 14},
            {'name': 'MongoDB', 'proficiency': 'advanced', 'years_experience': 3, 'category': 'databases', 'order': 15},
            {'name': 'Redis', 'proficiency': 'intermediate', 'years_experience': 2, 'category': 'databases', 'order': 16},

            # DevOps
            {'name': 'Docker', 'proficiency': 'advanced', 'years_experience': 3, 'category': 'devops', 'order': 17},
            {'name': 'AWS', 'proficiency': 'advanced', 'years_experience': 3, 'category': 'devops', 'order': 18},
            {'name': 'Git', 'proficiency': 'expert', 'years_experience': 5, 'category': 'devops', 'order': 19},
            {'name': 'GitHub Actions', 'proficiency': 'intermediate', 'years_experience': 2, 'category': 'devops', 'order': 20},
        ]

        skills = []
        for skill_data in skills_data:
            skill, created = Skill.objects.get_or_create(
                name=skill_data['name'],
                defaults=skill_data
            )
            skills.append(skill)
            if created:
                self.stdout.write(f'   ⚡ Created skill: {skill.name} ({skill.proficiency})')

        return skills

    def create_projects(self, project_types):
        """Create sample projects"""
        # Get some technologies for projects
        technologies = list(Technology.objects.all()[:20])  # Get first 20 technologies

        projects_data = [
            {
                'title': 'E-commerce Platform Advanced',
                'description': 'Plataforma completa de e-commerce con panel de administración, sistema de pagos, inventario y analytics en tiempo real.',
                'detailed_description': """
**E-commerce Platform Advanced** es una solución completa de comercio electrónico desarrollada desde cero con tecnologías modernas.

### Características Principales:
- **Frontend Responsivo**: Interfaz moderna desarrollada con React y Tailwind CSS
- **Backend Robusto**: API REST con Django y Django REST Framework
- **Pagos Seguros**: Integración con Stripe, PayPal y métodos de pago locales
- **Gestión de Inventario**: Sistema completo de stock, categorías y variantes de productos
- **Panel de Administración**: Dashboard interactivo con métricas en tiempo real
- **Optimización SEO**: Meta tags dinámicos y URLs amigables

### Tecnologías Utilizadas:
- **Backend**: Django, PostgreSQL, Redis, Celery
- **Frontend**: React, TypeScript, Tailwind CSS
- **Pagos**: Stripe API, PayPal SDK
- **Cloud**: AWS EC2, S3, CloudFront
- **Monitoreo**: Sentry, Google Analytics

### Resultados:
- **+500k usuarios** registrados en el primer año
- **99.9% uptime** con arquitectura cloud escalable
- **40% mejora** en conversión vs plataforma anterior
- **<2s tiempo de carga** en todas las páginas
                """,
                'github_url': 'https://github.com/alex-developer/ecommerce-advanced',
                'demo_url': 'https://ecommerce-demo.alexdev.com',
                'project_type_obj': project_types[4],  # E-commerce
                'featured': True,
                'order': 1,
                'visibility': 'public'
            },
            {
                'title': 'Analytics Dashboard Pro',
                'description': 'Dashboard interactivo para visualización de datos empresariales con gráficos en tiempo real y reportes automatizados.',
                'detailed_description': """
**Analytics Dashboard Pro** transforma datos complejos en insights accionables a través de visualizaciones interactivas.

### Funcionalidades Clave:
- **Visualizaciones Dinámicas**: Gráficos interactivos con Chart.js y D3.js
- **Tiempo Real**: WebSockets para actualizaciones automáticas de métricas
- **Reportes Automatizados**: Generación de PDFs programada
- **Multi-tenant**: Soporte para múltiples organizaciones
- **API Flexible**: Endpoints para integración con sistemas externos

### Stack Tecnológico:
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Vue.js 3, Vuex, Chart.js
- **WebSockets**: Socket.IO para tiempo real
- **Reportes**: ReportLab para PDFs
- **Deploy**: Docker + Kubernetes

### Impacto:
- **60% reducción** en tiempo de análisis de datos
- **+15 empresas** utilizando la plataforma
- **100% automatización** de reportes mensuales
                """,
                'github_url': 'https://github.com/alex-developer/analytics-dashboard',
                'demo_url': 'https://analytics.alexdev.com',
                'project_type_obj': project_types[3],  # Dashboard
                'featured': True,
                'order': 2,
                'visibility': 'public'
            },
            {
                'title': 'API REST Microservices',
                'description': 'Arquitectura de microservicios escalable con autenticación JWT, rate limiting y documentación automática.',
                'detailed_description': """
**API REST Microservices** es una arquitectura robusta diseñada para aplicaciones empresariales de gran escala.

### Arquitectura:
- **Microservicios**: Servicios independientes para Auth, Users, Products, Orders
- **API Gateway**: Kong para routing y rate limiting
- **Autenticación**: JWT con refresh tokens y roles
- **Documentación**: Swagger/OpenAPI automática
- **Monitoreo**: ELK Stack para logs y métricas

### Servicios Incluidos:
1. **Auth Service**: Autenticación y autorización
2. **User Service**: Gestión de perfiles y preferencias
3. **Product Service**: Catálogo y gestión de productos
4. **Order Service**: Procesamiento de pedidos
5. **Notification Service**: Emails y push notifications

### DevOps:
- **Containerización**: Docker con multi-stage builds
- **Orquestación**: Kubernetes con Helm charts
- **CI/CD**: GitHub Actions con testing automatizado
- **Monitoring**: Prometheus + Grafana

### Métricas:
- **<100ms** latencia promedio
- **10k+ requests/minuto** soportados
- **99.95% disponibilidad** en producción
                """,
                'github_url': 'https://github.com/alex-developer/api-microservices',
                'demo_url': 'https://api.alexdev.com/docs',
                'project_type_obj': project_types[1],  # API REST
                'featured': True,
                'order': 3,
                'visibility': 'public'
            },
            {
                'title': 'Task Automation Suite',
                'description': 'Suite de herramientas para automatización de tareas repetitivas con interfaz web y integración de APIs.',
                'detailed_description': """
**Task Automation Suite** elimina el trabajo manual a través de flujos automatizados inteligentes.

### Automatizaciones Disponibles:
- **Email Marketing**: Campañas automáticas basadas en comportamiento
- **Social Media**: Publicación programada en múltiples plataformas
- **Data Processing**: ETL automatizado para reportes
- **Backup & Sync**: Sincronización automática de archivos
- **Monitoring**: Alertas automáticas por métricas

### Integraciones:
- **APIs**: Slack, Twitter, Gmail, Google Drive, Dropbox
- **Webhooks**: Triggers basados en eventos externos
- **Schedulers**: Cron jobs y tareas programadas
- **Notifications**: Múltiples canales de notificación

### Tecnologías:
- **Backend**: Python, Celery, Redis, PostgreSQL
- **Frontend**: React, Material-UI
- **Queue System**: Redis + Celery para tareas asíncronas
- **Deploy**: Docker Swarm

### Resultados:
- **80% reducción** en tareas manuales
- **+50 flujos** automatizados diferentes
- **24/7 operación** sin intervención manual
                """,
                'github_url': 'https://github.com/alex-developer/automation-suite',
                'demo_url': 'https://automation.alexdev.com',
                'project_type_obj': project_types[5],  # Automatización
                'featured': False,
                'order': 4,
                'visibility': 'public'
            },
            {
                'title': 'Mobile App Backend',
                'description': 'Backend completo para aplicación móvil con push notifications, geolocalización y sincronización offline.',
                'detailed_description': """
**Mobile App Backend** proporciona una base sólida para aplicaciones móviles modernas con funcionalidades avanzadas.

### Características del Backend:
- **API RESTful**: Endpoints optimizados para móviles
- **Autenticación**: OAuth2 + JWT con biometría
- **Push Notifications**: FCM para Android e iOS
- **Geolocalización**: APIs de ubicación en tiempo real
- **Sincronización**: Offline-first con sync automático

### Funcionalidades Móviles:
- **Caching Inteligente**: Estrategias de caché para rendimiento
- **Compresión de Datos**: Optimización para conexiones lentas
- **Versionado de API**: Compatibilidad con múltiples versiones
- **Analytics**: Tracking de eventos y comportamiento
- **Crash Reporting**: Monitoreo de errores en tiempo real

### Stack:
- **API**: Django REST Framework + PostgreSQL
- **Cache**: Redis para sessions y datos temporales
- **Storage**: AWS S3 para archivos multimedia
- **Push**: Firebase Cloud Messaging
- **Monitor**: Sentry para error tracking

### Performance:
- **<200ms** respuesta API promedio
- **99.9% delivery rate** en notificaciones
- **Soporte offline** completo
                """,
                'github_url': 'https://github.com/alex-developer/mobile-backend',
                'demo_url': 'https://mobile-api.alexdev.com',
                'project_type_obj': project_types[2],  # Mobile App
                'featured': False,
                'order': 5,
                'visibility': 'public'
            },
            {
                'title': 'Portfolio Template System',
                'description': 'Sistema de templates para portfolios profesionales con CMS integrado y múltiples temas.',
                'detailed_description': """
**Portfolio Template System** permite a profesionales crear portfolios impresionantes sin conocimientos técnicos.

### Sistema de Templates:
- **Múltiples Temas**: +10 diseños profesionales
- **Customización Visual**: Editor drag & drop
- **Responsive Design**: Optimizado para todos los dispositivos
- **SEO Optimized**: Meta tags y estructura optimizada
- **Fast Loading**: <2s tiempo de carga

### CMS Integrado:
- **Editor WYSIWYG**: Creación de contenido visual
- **Gestión de Media**: Upload y organización de archivos
- **Blog System**: Sistema de blog integrado
- **Contact Forms**: Formularios personalizables
- **Analytics**: Dashboard de métricas incluido

### Características Técnicas:
- **Multi-tenant**: Múltiples portfolios en una instancia
- **CDN Integration**: Distribución global de contenido
- **Custom Domains**: Dominios personalizados
- **SSL**: Certificados automáticos
- **Backup**: Respaldos automáticos diarios

### Usuarios:
- **+200 portfolios** activos
- **95% satisfacción** de usuarios
- **<5 minutos** setup promedio
                """,
                'github_url': 'https://github.com/alex-developer/portfolio-system',
                'demo_url': 'https://portfolio-templates.alexdev.com',
                'project_type_obj': project_types[0],  # Web App
                'featured': False,
                'order': 6,
                'visibility': 'public'
            }
        ]

        projects = []
        for i, proj_data in enumerate(projects_data):
            project, created = Project.objects.get_or_create(
                title=proj_data['title'],
                defaults=proj_data
            )

            # Add random technologies to each project
            if created and technologies:
                project_techs = random.sample(technologies, min(8, len(technologies)))
                project.technologies.set(project_techs)

            projects.append(project)
            if created:
                self.stdout.write(f'   🚀 Created project: {project.title}')

        return projects

    def create_blog_posts(self, categories):
        """Create sample blog posts"""
        blog_posts_data = [
            {
                'title': 'Construyendo APIs Escalables con Django REST Framework',
                'slug': 'apis-escalables-django-rest-framework',
                'excerpt': 'Guía completa para desarrollar APIs REST robustas y escalables usando Django REST Framework, incluyendo mejores prácticas y optimizaciones.',
                'content': """
# Construyendo APIs Escalables con Django REST Framework

Django REST Framework (DRF) ha revolucionado la forma en que desarrollamos APIs en Python. En este artículo, exploraremos las mejores prácticas para crear APIs escalables y mantenibles.

## ¿Por qué Django REST Framework?

DRF ofrece una serie de ventajas que lo convierten en la elección ideal para APIs empresariales:

- **Serialización robusta**: Convierte automáticamente datos complejos a JSON
- **Autenticación integrada**: Múltiples métodos de autenticación out-of-the-box
- **Documentación automática**: Genera documentación interactiva automáticamente
- **Viewsets y Routers**: Reduce el código boilerplate significativamente

## Arquitectura Recomendada

### 1. Estructura del Proyecto

```python
myapi/
├── apps/
│   ├── users/
│   ├── products/
│   └── orders/
├── core/
│   ├── permissions.py
│   ├── pagination.py
│   └── exceptions.py
└── config/
    ├── settings/
    └── urls.py
```

### 2. Serializers Optimizados

```python
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category_name', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a cero")
        return value
```

## Optimizaciones de Performance

### 1. Uso de select_related y prefetch_related

```python
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category')\
                             .prefetch_related('reviews')
    serializer_class = ProductSerializer
```

### 2. Paginación Eficiente

```python
class CustomPageNumberPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
```

### 3. Caching Estratégico

```python
from django.core.cache import cache

class ProductViewSet(viewsets.ModelViewSet):
    def list(self, request):
        cache_key = f"products_list_{request.GET.urlencode()}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        # ... lógica normal
        cache.set(cache_key, data, timeout=300)  # 5 minutos
        return Response(data)
```

## Seguridad y Autenticación

### 1. JWT con Refresh Tokens

```python
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Log successful login
            logger.info(f"User {request.data.get('username')} logged in")

        return response
```

### 2. Permissions Granulares

```python
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
```

## Testing Comprehensivo

```python
class ProductAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@test.com', 'pass')
        self.client.force_authenticate(user=self.user)

    def test_create_product(self):
        data = {'name': 'Test Product', 'price': 99.99}
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, 201)
```

## Monitoreo y Logging

```python
import logging
from django.db import connection

logger = logging.getLogger(__name__)

class QueryCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        queries_before = len(connection.queries)
        response = self.get_response(request)
        queries_after = len(connection.queries)

        logger.info(f"View: {request.path} - Queries: {queries_after - queries_before}")
        return response
```

## Conclusión

Desarrollar APIs escalables requiere atención al detalle en múltiples aspectos: arquitectura, performance, seguridad y mantenibilidad. Django REST Framework proporciona las herramientas necesarias, pero la implementación correcta de estas prácticas es lo que marca la diferencia.

### Próximos Pasos

1. Implementa rate limiting con django-ratelimit
2. Configura monitoring con Sentry
3. Establece CI/CD con testing automatizado
4. Documenta tu API con drf-spectacular

¿Qué otras optimizaciones has implementado en tus APIs? Comparte tu experiencia en los comentarios.
                """,
                'category': categories[0],  # Desarrollo Web
                'reading_time': 8,
                'tags': 'django, api, rest, python, backend, escalabilidad',
                'status': 'published',
                'featured': True,
                'publish_date': timezone.now() - timedelta(days=2),
                'github_url': 'https://github.com/alex-developer/django-api-guide',
                'linkedin_url': 'https://linkedin.com/posts/alex-developer/django-apis'
            },
            {
                'title': 'Introducción al Machine Learning con Python',
                'slug': 'introduccion-machine-learning-python',
                'excerpt': 'Aprende los fundamentos del Machine Learning usando Python, desde la preparación de datos hasta la implementación de modelos predictivos.',
                'content': """
# Introducción al Machine Learning con Python

El Machine Learning se ha convertido en una habilidad esencial para desarrolladores y científicos de datos. En este tutorial, exploraremos los conceptos fundamentales y implementaremos nuestro primer modelo.

## ¿Qué es Machine Learning?

Machine Learning es una rama de la inteligencia artificial que permite a las computadoras aprender y tomar decisiones basadas en datos, sin ser explícitamente programadas para cada tarea específica.

### Tipos de Machine Learning

1. **Supervisado**: Aprende de datos etiquetados
2. **No Supervisado**: Encuentra patrones en datos sin etiquetas
3. **Por Refuerzo**: Aprende mediante recompensas y castigos

## Configurando el Entorno

```bash
pip install scikit-learn pandas numpy matplotlib seaborn jupyter
```

## Nuestro Primer Proyecto: Predicción de Precios de Casas

### 1. Importando Librerías

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
```

### 2. Cargando y Explorando Datos

```python
# Cargar datos
df = pd.read_csv('housing_data.csv')

# Exploración inicial
print(df.head())
print(df.info())
print(df.describe())

# Verificar valores nulos
print(df.isnull().sum())
```

### 3. Visualización de Datos

```python
# Matriz de correlación
plt.figure(figsize=(12, 8))
correlation_matrix = df.corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.title('Matriz de Correlación')
plt.show()

# Distribución del precio
plt.figure(figsize=(10, 6))
plt.hist(df['price'], bins=50, alpha=0.7)
plt.xlabel('Precio')
plt.ylabel('Frecuencia')
plt.title('Distribución de Precios')
plt.show()
```

### 4. Preparación de Datos

```python
# Seleccionar características
features = ['size', 'bedrooms', 'bathrooms', 'age', 'location_score']
X = df[features]
y = df['price']

# Dividir datos en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Datos de entrenamiento: {X_train.shape}")
print(f"Datos de prueba: {X_test.shape}")
```

### 5. Entrenando el Modelo

```python
# Crear y entrenar el modelo
model = LinearRegression()
model.fit(X_train, y_train)

# Realizar predicciones
y_pred = model.predict(X_test)

# Evaluar el modelo
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Error Cuadrático Medio: {mse:.2f}")
print(f"R² Score: {r2:.2f}")
```

### 6. Interpretando Resultados

```python
# Importancia de características
feature_importance = pd.DataFrame({
    'feature': features,
    'coefficient': model.coef_
})
feature_importance = feature_importance.sort_values('coefficient', key=abs, ascending=False)

print("Importancia de Características:")
print(feature_importance)

# Visualizar predicciones vs valores reales
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, alpha=0.7)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.xlabel('Precio Real')
plt.ylabel('Precio Predicho')
plt.title('Predicciones vs Valores Reales')
plt.show()
```

## Mejorando el Modelo

### 1. Feature Engineering

```python
# Crear nuevas características
df['price_per_sqft'] = df['price'] / df['size']
df['bathroom_bedroom_ratio'] = df['bathrooms'] / df['bedrooms']

# Transformaciones logarítmicas
df['log_price'] = np.log(df['price'])
df['log_size'] = np.log(df['size'])
```

### 2. Modelos Más Avanzados

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score

# Random Forest
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Validación cruzada
cv_scores = cross_val_score(rf_model, X_train, y_train, cv=5)
print(f"CV Score promedio: {cv_scores.mean():.2f} (+/- {cv_scores.std() * 2:.2f})")
```

### 3. Optimización de Hiperparámetros

```python
from sklearn.model_selection import GridSearchCV

# Definir grid de parámetros
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10]
}

# Grid search
grid_search = GridSearchCV(
    RandomForestRegressor(random_state=42),
    param_grid,
    cv=5,
    scoring='r2'
)

grid_search.fit(X_train, y_train)
print(f"Mejores parámetros: {grid_search.best_params_}")
```

## Implementación en Producción

### 1. Guardando el Modelo

```python
import joblib

# Guardar modelo entrenado
joblib.dump(model, 'house_price_model.pkl')

# Cargar modelo
loaded_model = joblib.load('house_price_model.pkl')
```

### 2. API para Predicciones

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
model = joblib.load('house_price_model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    features = np.array(data['features']).reshape(1, -1)
    prediction = model.predict(features)[0]

    return jsonify({'prediction': float(prediction)})

if __name__ == '__main__':
    app.run(debug=True)
```

## Próximos Pasos

1. **Deep Learning**: Explora redes neuronales con TensorFlow/PyTorch
2. **Time Series**: Aprende forecasting para datos temporales
3. **Computer Vision**: Implementa clasificación de imágenes
4. **NLP**: Procesamiento de lenguaje natural

## Recursos Adicionales

- [Scikit-learn Documentation](https://scikit-learn.org/)
- [Kaggle Learn](https://www.kaggle.com/learn)
- [Coursera ML Course](https://www.coursera.org/learn/machine-learning)

¿Qué tipo de proyecto de ML te gustaría explorar siguiente? ¡Comparte tus ideas en los comentarios!
                """,
                'category': categories[1],  # IA
                'reading_time': 12,
                'tags': 'machine-learning, python, ai, data-science, sklearn',
                'status': 'published',
                'featured': True,
                'publish_date': timezone.now() - timedelta(days=5),
                'github_url': 'https://github.com/alex-developer/ml-tutorial'
            },
            {
                'title': 'DevOps Essentials: Docker y Kubernetes en Producción',
                'slug': 'devops-docker-kubernetes-produccion',
                'excerpt': 'Guía práctica para implementar Docker y Kubernetes en entornos de producción, incluyendo mejores prácticas y monitoreo.',
                'content': """
# DevOps Essentials: Docker y Kubernetes en Producción

La containerización ha transformado la forma en que desplegamos aplicaciones. En esta guía, exploraremos cómo llevar Docker y Kubernetes a producción de manera exitosa.

## Fundamentos de Docker

### 1. Dockerfile Optimizado

```dockerfile
# Multi-stage build para Python
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

# Crear usuario no-root
RUN useradd --create-home --shell /bin/bash app

# Copiar dependencias desde builder
COPY --from=builder /root/.local /home/app/.local

# Configurar PATH
ENV PATH=/home/app/.local/bin:$PATH

WORKDIR /app
COPY . .

# Cambiar a usuario no-root
USER app

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:application"]
```

### 2. Docker Compose para Desarrollo

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=1
      - DATABASE_URL=postgresql://user:pass@db:5432/myapp
    volumes:
      - .:/app
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Kubernetes en Producción

### 1. Deployment Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-deployment
  labels:
    app: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: myapp-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 2. Service y Ingress

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  selector:
    app: myapp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - myapp.example.com
    secretName: myapp-tls
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp-service
            port:
              number: 80
```

### 3. ConfigMaps y Secrets

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
data:
  REDIS_HOST: redis-service
  REDIS_PORT: "6379"
  LOG_LEVEL: "INFO"

---
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secrets
type: Opaque
data:
  database-url: <base64-encoded-database-url>
  secret-key: <base64-encoded-secret-key>
```

## CI/CD Pipeline

### 1. GitHub Actions Workflow

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest coverage

    - name: Run tests
      run: |
        coverage run -m pytest
        coverage report

    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v3

    - name: Build Docker image
      run: |
        docker build -t myapp:${{ github.sha }} .
        docker tag myapp:${{ github.sha }} myapp:latest

    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push myapp:${{ github.sha }}
        docker push myapp:latest

    - name: Deploy to Kubernetes
      run: |
        echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
        kubectl set image deployment/myapp-deployment myapp=myapp:${{ github.sha }}
        kubectl rollout status deployment/myapp-deployment
```

## Monitoreo y Observabilidad

### 1. Prometheus Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s

    scrape_configs:
    - job_name: 'kubernetes-apiservers'
      kubernetes_sd_configs:
      - role: endpoints
      scheme: https
      tls_config:
        ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
      relabel_configs:
      - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
        action: keep
        regex: default;kubernetes;https

    - job_name: 'myapp'
      kubernetes_sd_configs:
      - role: pod
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: myapp
```

### 2. Grafana Dashboard

```json
{
  "dashboard": {
    "title": "MyApp Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{ method }} {{ status }}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

## Seguridad en Contenedores

### 1. Security Context

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
  containers:
  - name: app
    image: myapp:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
    volumeMounts:
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: tmp
    emptyDir: {}
```

### 2. Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: myapp-netpol
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx-ingress
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
```

## Gestión de Recursos

### 1. Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp-deployment
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 2. Resource Quotas

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: myapp-quota
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "10"
    services: "5"
```

## Mejores Prácticas

### 1. Imagen Base Minimal

```dockerfile
FROM gcr.io/distroless/python3-debian11

COPY --from=builder /app /app
WORKDIR /app

EXPOSE 8000
ENTRYPOINT ["python", "app.py"]
```

### 2. Health Checks

```python
@app.route('/health')
def health_check():
    try:
        # Verificar conexión a base de datos
        db.execute('SELECT 1')
        return {'status': 'healthy'}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 503

@app.route('/ready')
def readiness_check():
    if app_ready:
        return {'status': 'ready'}, 200
    return {'status': 'not ready'}, 503
```

## Troubleshooting Común

### 1. Debugging Pods

```bash
# Ver logs del pod
kubectl logs -f pod-name

# Ejecutar shell en pod
kubectl exec -it pod-name -- /bin/sh

# Describir pod para eventos
kubectl describe pod pod-name

# Port forwarding para debug
kubectl port-forward pod-name 8080:8000
```

### 2. Análisis de Recursos

```bash
# Top pods por CPU/memoria
kubectl top pods

# Eventos del cluster
kubectl get events --sort-by='.lastTimestamp'

# Estado de nodos
kubectl describe nodes
```

## Conclusión

Implementar Docker y Kubernetes en producción requiere atención a múltiples aspectos: seguridad, monitoreo, escalabilidad y mantenibilidad. Las herramientas y prácticas mostradas aquí proporcionan una base sólida para operaciones exitosas.

### Próximos Pasos

1. Implementa service mesh con Istio
2. Configura disaster recovery
3. Automatiza security scanning
4. Establece compliance monitoring

¿Qué desafíos has enfrentado con Kubernetes en producción? Comparte tu experiencia en los comentarios.
                """,
                'category': categories[2],  # DevOps
                'reading_time': 15,
                'tags': 'devops, docker, kubernetes, containers, production, monitoring',
                'status': 'published',
                'featured': True,
                'publish_date': timezone.now() - timedelta(days=7),
                'github_url': 'https://github.com/alex-developer/k8s-production-guide'
            },
            {
                'title': 'React Hooks Avanzados: Creando Hooks Personalizados',
                'slug': 'react-hooks-avanzados-personalizados',
                'excerpt': 'Explora el poder de los hooks personalizados en React para crear componentes más reutilizables y maintener un código más limpio.',
                'content': """
# React Hooks Avanzados: Creando Hooks Personalizados

Los hooks personalizados son una de las características más poderosas de React. Nos permiten extraer lógica de componentes en funciones reutilizables.

## ¿Qué son los Hooks Personalizados?

Un hook personalizado es una función de JavaScript cuyo nombre comienza con "use" y que puede llamar a otros hooks.

### Ejemplo Básico: useLocalStorage

```javascript
import { useState, useEffect } from 'react';

function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue];
}

// Uso del hook
function MyComponent() {
  const [name, setName] = useLocalStorage('name', '');

  return (
    <input
      value={name}
      onChange={(e) => setName(e.target.value)}
      placeholder="Tu nombre"
    />
  );
}
```

## Hooks para Gestión de Estado

### useReducer Avanzado

```javascript
import { useReducer, useCallback } from 'react';

function useUndoableState(initialState) {
  const [state, dispatch] = useReducer((state, action) => {
    switch (action.type) {
      case 'SET':
        return {
          past: [...state.past, state.present],
          present: action.payload,
          future: []
        };
      case 'UNDO':
        if (state.past.length === 0) return state;

        return {
          past: state.past.slice(0, -1),
          present: state.past[state.past.length - 1],
          future: [state.present, ...state.future]
        };
      case 'REDO':
        if (state.future.length === 0) return state;

        return {
          past: [...state.past, state.present],
          present: state.future[0],
          future: state.future.slice(1)
        };
      case 'RESET':
        return {
          past: [],
          present: initialState,
          future: []
        };
      default:
        return state;
    }
  }, {
    past: [],
    present: initialState,
    future: []
  });

  const setState = useCallback((newState) => {
    dispatch({ type: 'SET', payload: newState });
  }, []);

  const undo = useCallback(() => {
    dispatch({ type: 'UNDO' });
  }, []);

  const redo = useCallback(() => {
    dispatch({ type: 'REDO' });
  }, []);

  const reset = useCallback(() => {
    dispatch({ type: 'RESET' });
  }, []);

  return {
    state: state.present,
    setState,
    undo,
    redo,
    reset,
    canUndo: state.past.length > 0,
    canRedo: state.future.length > 0
  };
}
```

## Hooks para APIs y Data Fetching

### useFetch Completo

```javascript
import { useState, useEffect, useRef, useCallback } from 'react';

function useFetch(url, options = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const controllerRef = useRef(null);

  const execute = useCallback(async (customUrl = url, customOptions = {}) => {
    try {
      setLoading(true);
      setError(null);

      // Cancelar request anterior si existe
      if (controllerRef.current) {
        controllerRef.current.abort();
      }

      // Crear nuevo AbortController
      controllerRef.current = new AbortController();

      const response = await fetch(customUrl, {
        signal: controllerRef.current.signal,
        ...options,
        ...customOptions,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
          ...customOptions.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setData(result);
      return result;
    } catch (error) {
      if (error.name !== 'AbortError') {
        setError(error.message);
        throw error;
      }
    } finally {
      setLoading(false);
    }
  }, [url, options]);

  const cancel = useCallback(() => {
    if (controllerRef.current) {
      controllerRef.current.abort();
    }
  }, []);

  useEffect(() => {
    if (url) {
      execute();
    }

    return () => {
      cancel();
    };
  }, [url, execute, cancel]);

  return { data, loading, error, execute, cancel };
}

// Hook para mutations (POST, PUT, DELETE)
function useMutation(mutationFn) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const mutate = useCallback(async (...args) => {
    try {
      setLoading(true);
      setError(null);
      const result = await mutationFn(...args);
      setData(result);
      return result;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [mutationFn]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return { data, loading, error, mutate, reset };
}
```

## Hooks para UI y Interacciones

### useIntersectionObserver

```javascript
import { useState, useEffect, useRef } from 'react';

function useIntersectionObserver(options = {}) {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const [entry, setEntry] = useState(null);
  const elementRef = useRef(null);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(([entry]) => {
      setIsIntersecting(entry.isIntersecting);
      setEntry(entry);
    }, {
      threshold: 0.1,
      rootMargin: '0px',
      ...options,
    });

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [options]);

  return [elementRef, isIntersecting, entry];
}

// Uso para lazy loading
function LazyImage({ src, alt }) {
  const [imgRef, isVisible] = useIntersectionObserver({
    threshold: 0.1,
    rootMargin: '50px',
  });

  return (
    <div ref={imgRef}>
      {isVisible ? (
        <img src={src} alt={alt} />
      ) : (
        <div>Loading...</div>
      )}
    </div>
  );
}
```

### useClickOutside

```javascript
import { useEffect, useRef } from 'react';

function useClickOutside(handler) {
  const ref = useRef(null);

  useEffect(() => {
    const handleClick = (event) => {
      if (ref.current && !ref.current.contains(event.target)) {
        handler();
      }
    };

    document.addEventListener('mousedown', handleClick);
    document.addEventListener('touchstart', handleClick);

    return () => {
      document.removeEventListener('mousedown', handleClick);
      document.removeEventListener('touchstart', handleClick);
    };
  }, [handler]);

  return ref;
}

// Componente de Modal usando el hook
function Modal({ isOpen, onClose, children }) {
  const modalRef = useClickOutside(onClose);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div ref={modalRef} className="modal-content">
        {children}
      </div>
    </div>
  );
}
```

## Hooks para Performance

### useDebounce

```javascript
import { useState, useEffect } from 'react';

function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// Componente de búsqueda con debounce
function SearchComponent() {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearchTerm = useDebounce(searchTerm, 500);
  const { data: results, loading } = useFetch(
    debouncedSearchTerm ? `/api/search?q=${debouncedSearchTerm}` : null
  );

  return (
    <div>
      <input
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Buscar..."
      />
      {loading && <div>Buscando...</div>}
      {results && (
        <ul>
          {results.map(item => (
            <li key={item.id}>{item.name}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

### useThrottle

```javascript
import { useState, useEffect, useRef } from 'react';

function useThrottle(value, interval) {
  const [throttledValue, setThrottledValue] = useState(value);
  const lastExecuted = useRef(Date.now());

  useEffect(() => {
    if (Date.now() >= lastExecuted.current + interval) {
      lastExecuted.current = Date.now();
      setThrottledValue(value);
    } else {
      const timerId = setTimeout(() => {
        lastExecuted.current = Date.now();
        setThrottledValue(value);
      }, interval);

      return () => clearTimeout(timerId);
    }
  }, [value, interval]);

  return throttledValue;
}
```

## Hook para Gestión de Formularios

### useForm

```javascript
import { useState, useCallback } from 'react';

function useForm(initialValues = {}, validationRules = {}) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  const validate = useCallback((fieldName, value) => {
    const rules = validationRules[fieldName];
    if (!rules) return '';

    for (const rule of rules) {
      const error = rule(value, values);
      if (error) return error;
    }
    return '';
  }, [validationRules, values]);

  const setValue = useCallback((name, value) => {
    setValues(prev => ({ ...prev, [name]: value }));

    if (touched[name]) {
      const error = validate(name, value);
      setErrors(prev => ({ ...prev, [name]: error }));
    }
  }, [touched, validate]);

  const setFieldTouched = useCallback((name) => {
    setTouched(prev => ({ ...prev, [name]: true }));
    const error = validate(name, values[name]);
    setErrors(prev => ({ ...prev, [name]: error }));
  }, [validate, values]);

  const handleChange = useCallback((e) => {
    const { name, value, type, checked } = e.target;
    setValue(name, type === 'checkbox' ? checked : value);
  }, [setValue]);

  const handleBlur = useCallback((e) => {
    setFieldTouched(e.target.name);
  }, [setFieldTouched]);

  const validateAll = useCallback(() => {
    const newErrors = {};
    let isValid = true;

    Object.keys(validationRules).forEach(fieldName => {
      const error = validate(fieldName, values[fieldName]);
      newErrors[fieldName] = error;
      if (error) isValid = false;
    });

    setErrors(newErrors);
    setTouched(Object.keys(validationRules).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {}));

    return isValid;
  }, [validationRules, validate, values]);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  }, [initialValues]);

  return {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    setValue,
    setFieldTouched,
    validateAll,
    reset,
    isValid: Object.values(errors).every(error => !error)
  };
}

// Validadores comunes
const validators = {
  required: (value) => !value ? 'Este campo es requerido' : '',
  email: (value) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return value && !emailRegex.test(value) ? 'Email inválido' : '';
  },
  minLength: (min) => (value) =>
    value && value.length < min ? `Mínimo ${min} caracteres` : '',
};

// Uso del hook de formulario
function ContactForm() {
  const { values, errors, touched, handleChange, handleBlur, validateAll, reset } = useForm(
    { name: '', email: '', message: '' },
    {
      name: [validators.required],
      email: [validators.required, validators.email],
      message: [validators.required, validators.minLength(10)],
    }
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateAll()) {
      console.log('Form submitted:', values);
      reset();
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        name="name"
        value={values.name}
        onChange={handleChange}
        onBlur={handleBlur}
        placeholder="Nombre"
      />
      {touched.name && errors.name && <span>{errors.name}</span>}

      <input
        name="email"
        value={values.email}
        onChange={handleChange}
        onBlur={handleBlur}
        placeholder="Email"
      />
      {touched.email && errors.email && <span>{errors.email}</span>}

      <textarea
        name="message"
        value={values.message}
        onChange={handleChange}
        onBlur={handleBlur}
        placeholder="Mensaje"
      />
      {touched.message && errors.message && <span>{errors.message}</span>}

      <button type="submit">Enviar</button>
    </form>
  );
}
```

## Testing de Hooks Personalizados

```javascript
import { renderHook, act } from '@testing-library/react';
import { useLocalStorage } from './useLocalStorage';

describe('useLocalStorage', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test('should initialize with initial value', () => {
    const { result } = renderHook(() => useLocalStorage('test', 'initial'));
    expect(result.current[0]).toBe('initial');
  });

  test('should update localStorage when value changes', () => {
    const { result } = renderHook(() => useLocalStorage('test', 'initial'));

    act(() => {
      result.current[1]('updated');
    });

    expect(result.current[0]).toBe('updated');
    expect(localStorage.getItem('test')).toBe('"updated"');
  });

  test('should load value from localStorage', () => {
    localStorage.setItem('test', '"stored"');

    const { result } = renderHook(() => useLocalStorage('test', 'initial'));
    expect(result.current[0]).toBe('stored');
  });
});
```

## Mejores Prácticas

### 1. Nomenclatura Clara

```javascript
// ✅ Bueno: nombre descriptivo
function useApiData(url) { }

// ❌ Malo: nombre genérico
function useData(url) { }
```

### 2. Retorno Consistente

```javascript
// ✅ Bueno: objeto con propiedades nombradas
function useApi(url) {
  return { data, loading, error, refetch };
}

// ✅ También bueno: array para valores simples
function useToggle(initial = false) {
  return [value, toggle, setValue];
}
```

### 3. Manejo de Dependencies

```javascript
// ✅ Bueno: dependencies explícitas
function useApi(url, options) {
  const optionsRef = useRef(options);

  useEffect(() => {
    optionsRef.current = options;
  });

  useEffect(() => {
    fetchData(url, optionsRef.current);
  }, [url]); // Solo url como dependency
}
```

## Conclusión

Los hooks personalizados son una herramienta poderosa para crear código React más limpio, reutilizable y testeable. Permiten extraer lógica compleja en funciones simples que pueden ser compartidas entre componentes.

### Próximos Pasos

1. Crea una librería de hooks personalizados para tu equipo
2. Explora hooks de librerías como react-query, react-hook-form
3. Implementa hooks para casos específicos de tu aplicación
4. Contribuye a librerías open source de hooks

¿Qué hooks personalizados has creado en tus proyectos? ¡Comparte tus experiencias en los comentarios!
                """,
                'category': categories[0],  # Desarrollo Web
                'reading_time': 10,
                'tags': 'react, hooks, javascript, frontend, reusability',
                'status': 'published',
                'featured': False,
                'publish_date': timezone.now() - timedelta(days=10)
            },
            {
                'title': 'El Futuro del Desarrollo: Tendencias Tecnológicas 2024',
                'slug': 'futuro-desarrollo-tendencias-2024',
                'excerpt': 'Análisis de las principales tendencias tecnológicas que están moldeando el futuro del desarrollo de software en 2024 y más allá.',
                'content': """
# El Futuro del Desarrollo: Tendencias Tecnológicas 2024

La industria del desarrollo de software evoluciona a un ritmo vertiginoso. Analicemos las tendencias más importantes que están definiendo el panorama tecnológico actual.

## 1. Inteligencia Artificial Generativa

### Copilots de Código
La IA está revolucionando cómo escribimos código:

- **GitHub Copilot**: Autocompletado inteligente
- **Tabnine**: Sugerencias basadas en contexto
- **Cursor**: IDE completo con IA integrada

### Impacto en el Desarrollo
```python
# Antes: escribir todo manualmente
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Con IA: comentario → código automático
# "Generate a memoized fibonacci function"
def fibonacci_memo(n, cache={}):
    if n in cache:
        return cache[n]
    if n <= 1:
        cache[n] = n
    else:
        cache[n] = fibonacci_memo(n-1, cache) + fibonacci_memo(n-2, cache)
    return cache[n]
```

## 2. Edge Computing y Serverless

### Vercel Functions
```javascript
// api/hello.js
export default function handler(req, res) {
  res.status(200).json({
    message: 'Hello from the edge!',
    region: process.env.VERCEL_REGION
  });
}
```

### Cloudflare Workers
```javascript
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (url.pathname === '/api/data') {
      // Procesamiento en edge, cerca del usuario
      return new Response(JSON.stringify({
        data: 'Processed at edge location'
      }), {
        headers: { 'content-type': 'application/json' },
      });
    }

    return new Response('Not found', { status: 404 });
  },
};
```

## 3. WebAssembly (WASM)

### Rendimiento Nativo en el Browser
```rust
// lib.rs - Función Rust compilada a WASM
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn process_image(data: &[u8]) -> Vec<u8> {
    // Procesamiento intensivo de imagen
    // 10x más rápido que JavaScript
    data.iter()
        .map(|&pixel| if pixel > 128 { 255 } else { 0 })
        .collect()
}
```

```javascript
// main.js
import init, { process_image } from './pkg/image_processor.js';

async function processImage(imageData) {
  await init();
  return process_image(imageData);
}
```

## 4. Micro-Frontends

### Module Federation
```javascript
// webpack.config.js - Host Application
const ModuleFederationPlugin = require('@module-federation/webpack');

module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'host',
      remotes: {
        mfe1: 'mfe1@http://localhost:3001/remoteEntry.js',
        mfe2: 'mfe2@http://localhost:3002/remoteEntry.js',
      },
    }),
  ],
};

// App.jsx
import React, { Suspense } from 'react';
const RemoteComponent = React.lazy(() => import('mfe1/Component'));

function App() {
  return (
    <div>
      <h1>Host Application</h1>
      <Suspense fallback={<div>Loading...</div>}>
        <RemoteComponent />
      </Suspense>
    </div>
  );
}
```

## 5. Low-Code/No-Code Evolution

### Plataformas Emergentes
- **Retool**: Dashboards empresariales
- **Bubble**: Aplicaciones web completas
- **Zapier**: Automatización visual
- **Supabase**: Backend-as-a-Service

### Integración con Código Tradicional
```typescript
// Supabase + TypeScript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
);

// Auto-generated types from database schema
interface User {
  id: string;
  email: string;
  created_at: string;
}

async function getUsers(): Promise<User[]> {
  const { data, error } = await supabase
    .from('users')
    .select('*');

  if (error) throw error;
  return data;
}
```

## 6. Web3 y Blockchain

### Smart Contracts con Solidity
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract SimpleStorage {
    uint256 private storedData;

    event DataStored(uint256 indexed value, address indexed sender);

    function set(uint256 x) public {
        storedData = x;
        emit DataStored(x, msg.sender);
    }

    function get() public view returns (uint256) {
        return storedData;
    }
}
```

### Integración Web3
```javascript
// web3-integration.js
import { ethers } from 'ethers';

class Web3Service {
  constructor() {
    this.provider = new ethers.providers.Web3Provider(window.ethereum);
    this.signer = this.provider.getSigner();
  }

  async connectWallet() {
    await window.ethereum.request({ method: 'eth_requestAccounts' });
    const address = await this.signer.getAddress();
    return address;
  }

  async callContract(contractAddress, abi, method, ...args) {
    const contract = new ethers.Contract(contractAddress, abi, this.signer);
    return await contract[method](...args);
  }
}
```

## 7. Advanced TypeScript

### Template Literal Types
```typescript
type EmailValidation<T extends string> = T extends `${string}@${string}.${string}`
  ? T
  : never;

type ValidEmail = EmailValidation<'user@example.com'>; // ✅
type InvalidEmail = EmailValidation<'invalid-email'>; // ❌ never

// Utility types avanzados
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object
    ? DeepReadonly<T[P]>
    : T[P];
};

type ApiResponse<T> = {
  data: T;
  status: 'success' | 'error';
  message?: string;
};

// Type-safe API calls
async function fetchUser(id: string): Promise<ApiResponse<User>> {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
}
```

## 8. Advanced CSS

### Container Queries
```css
/* Responsive basado en el contenedor, no en el viewport */
.card-container {
  container-type: inline-size;
}

@container (min-width: 300px) {
  .card {
    display: grid;
    grid-template-columns: 1fr 2fr;
  }
}

@container (min-width: 500px) {
  .card {
    grid-template-columns: 1fr 1fr 1fr;
  }
}
```

### CSS Cascade Layers
```css
@layer reset, base, components, utilities;

@layer reset {
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
}

@layer base {
  body {
    font-family: system-ui;
    line-height: 1.5;
  }
}

@layer components {
  .btn {
    padding: 0.5rem 1rem;
    border: 1px solid currentColor;
    border-radius: 0.25rem;
  }
}
```

## 9. Performance Monitoring

### Core Web Vitals
```javascript
// performance-monitoring.js
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  // Enviar métricas a servicio de analytics
  gtag('event', metric.name, {
    value: Math.round(metric.value),
    event_category: 'Web Vitals',
    non_interaction: true,
  });
}

// Monitorear todas las métricas importantes
getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

### Real User Monitoring (RUM)
```typescript
class PerformanceTracker {
  private observer: PerformanceObserver;

  constructor() {
    this.observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        this.processEntry(entry);
      }
    });

    this.observer.observe({ entryTypes: ['navigation', 'resource', 'paint'] });
  }

  private processEntry(entry: PerformanceEntry) {
    if (entry.entryType === 'navigation') {
      const nav = entry as PerformanceNavigationTiming;
      this.trackNavigation({
        dns: nav.domainLookupEnd - nav.domainLookupStart,
        tcp: nav.connectEnd - nav.connectStart,
        ttfb: nav.responseStart - nav.requestStart,
        dom: nav.domContentLoadedEventEnd - nav.responseEnd,
      });
    }
  }

  private trackNavigation(timing: any) {
    // Enviar datos a servicio de monitoreo
    fetch('/api/performance', {
      method: 'POST',
      body: JSON.stringify(timing),
    });
  }
}
```

## 10. Security-First Development

### Content Security Policy
```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: https:",
      "font-src 'self' https://fonts.gstatic.com",
      "connect-src 'self' https://api.example.com",
    ].join('; '),
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY',
  },
];

module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
    ];
  },
};
```

### Secure Authentication
```typescript
// auth-service.ts
import { SignJWT, jwtVerify } from 'jose';
import { scrypt, randomBytes } from 'crypto';
import { promisify } from 'util';

const scryptAsync = promisify(scrypt);

export class AuthService {
  private secret = new TextEncoder().encode(process.env.JWT_SECRET);

  async hashPassword(password: string): Promise<string> {
    const salt = randomBytes(16).toString('hex');
    const hash = (await scryptAsync(password, salt, 64)) as Buffer;
    return `${salt}:${hash.toString('hex')}`;
  }

  async verifyPassword(password: string, hashedPassword: string): Promise<boolean> {
    const [salt, hash] = hashedPassword.split(':');
    const verifyHash = (await scryptAsync(password, salt, 64)) as Buffer;
    return hash === verifyHash.toString('hex');
  }

  async generateToken(payload: any): Promise<string> {
    return await new SignJWT(payload)
      .setProtectedHeader({ alg: 'HS256' })
      .setIssuedAt()
      .setExpirationTime('2h')
      .sign(this.secret);
  }

  async verifyToken(token: string): Promise<any> {
    const { payload } = await jwtVerify(token, this.secret);
    return payload;
  }
}
```

## Tendencias Emergentes para 2025

### 1. Quantum Computing
```python
# Quantum development con Qiskit
from qiskit import QuantumCircuit, execute, Aer

def quantum_random_number():
    circuit = QuantumCircuit(1, 1)
    circuit.h(0)  # Superposición
    circuit.measure(0, 0)

    backend = Aer.get_backend('qasm_simulator')
    job = execute(circuit, backend, shots=1)
    result = job.result()
    counts = result.get_counts(circuit)

    return int(list(counts.keys())[0])
```

### 2. Neuromorphic Computing
```javascript
// Brain.js para redes neuronales en JavaScript
import brain from 'brain.js';

const net = new brain.NeuralNetwork();

net.train([
  { input: [0, 0], output: [0] },
  { input: [0, 1], output: [1] },
  { input: [1, 0], output: [1] },
  { input: [1, 1], output: [0] }
]);

const output = net.run([1, 0]); // XOR gate
```

## Impacto en la Industria

### Cambios en Roles de Desarrollador

**Nuevas Especialidades:**
- **AI/ML Engineers**: Especialistas en integración de IA
- **DevOps/Platform Engineers**: Infraestructura cloud-native
- **Web3 Developers**: Aplicaciones descentralizadas
- **Performance Engineers**: Optimización UX/Core Web Vitals

### Skills del Futuro

1. **Prompt Engineering**: Trabajar efectivamente con IA
2. **Edge Computing**: Distribución global de aplicaciones
3. **Security-First**: Desarrollo seguro por defecto
4. **Performance Optimization**: Core Web Vitals y UX
5. **Cross-Platform**: Una base de código, múltiples plataformas

## Conclusión

El desarrollo de software en 2024 se caracteriza por:

- **Democratización**: IA y low-code hacen el desarrollo más accesible
- **Performance**: Edge computing y WebAssembly mejoran la velocidad
- **Descentralización**: Web3 y blockchain cambian paradigmas
- **Seguridad**: Security-first se vuelve estándar
- **Automatización**: CI/CD y testing automatizado

### Recomendaciones para Desarrolladores

1. **Experimenta con IA**: Integra copilots en tu workflow
2. **Aprende WebAssembly**: Para aplicaciones de alto rendimiento
3. **Domina TypeScript**: Type safety es el futuro
4. **Practica DevOps**: Infrastructure as Code es esencial
5. **Mantente actualizado**: La industria evoluciona rapidamente

¿Qué tendencia te parece más prometedora? ¿Cuáles estás implementando ya en tus proyectos? Comparte tu perspectiva en los comentarios.
                """,
                'category': categories[4],  # Opinión
                'reading_time': 18,
                'tags': 'tendencias, futuro, desarrollo, tecnologia, 2024, ai, web3',
                'status': 'published',
                'featured': False,
                'publish_date': timezone.now() - timedelta(days=3)
            }
        ]

        blog_posts = []
        for post_data in blog_posts_data:
            blog_post, created = BlogPost.objects.get_or_create(
                slug=post_data['slug'],
                defaults=post_data
            )
            blog_posts.append(blog_post)
            if created:
                self.stdout.write(f'   📝 Created blog post: {blog_post.title}')

        return blog_posts

    def create_sample_contacts(self):
        """Create sample contact messages"""
        contacts_data = [
            {
                'name': 'María González',
                'email': 'maria@example.com',
                'subject': 'Consulta sobre proyecto Django',
                'message': 'Hola Alex, vi tu portafolio y me interesa mucho tu experiencia con Django. ¿Podrías contarme más sobre tus proyectos de e-commerce? Estamos buscando desarrollar una plataforma similar.',
                'created_at': timezone.now() - timedelta(days=1),
                'read': False
            },
            {
                'name': 'Carlos Rodríguez',
                'email': 'carlos.dev@email.com',
                'subject': 'Propuesta de colaboración',
                'message': 'Excelente trabajo en tu blog sobre APIs escalables. Soy CTO de una startup y nos gustaría discutir una posible colaboración. ¿Tendrías tiempo para una llamada esta semana?',
                'created_at': timezone.now() - timedelta(days=3),
                'read': True
            },
            {
                'name': 'Ana Martínez',
                'email': 'ana.martinez@company.com',
                'subject': 'Oportunidad laboral - Senior Developer',
                'message': 'Buenos días Alex, soy recruitera de TechCorp y hemos revisado tu perfil. Tenemos una posición de Senior Full Stack Developer que podría interesarte. ¿Estarías disponible para una entrevista?',
                'created_at': timezone.now() - timedelta(days=5),
                'read': True
            },
            {
                'name': 'Diego López',
                'email': 'diego@freelance.com',
                'subject': 'Pregunta sobre React Hooks',
                'message': 'Hola! Leí tu artículo sobre hooks personalizados y me surgió una duda sobre el hook useForm que propones. ¿Cómo manejarías validaciones asíncronas? Gracias por compartir tan buen contenido.',
                'created_at': timezone.now() - timedelta(days=7),
                'read': False
            },
            {
                'name': 'Sara Johnson',
                'email': 'sara@international.com',
                'subject': 'Remote work opportunity',
                'message': 'Hi Alex, I found your portfolio through GitHub and I\'m impressed by your microservices project. We\'re a US-based company looking for remote Django developers. Would you be interested in discussing a position?',
                'created_at': timezone.now() - timedelta(days=10),
                'read': True
            }
        ]

        contacts = []
        for contact_data in contacts_data:
            contact, created = Contact.objects.get_or_create(
                email=contact_data['email'],
                subject=contact_data['subject'],
                defaults=contact_data
            )
            contacts.append(contact)
            if created:
                self.stdout.write(f'   📧 Created contact: {contact.name} - {contact.subject}')

        return contacts