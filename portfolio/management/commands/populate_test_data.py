"""
Comando unificado para poblar todos los datos de prueba del portfolio.
Incluye: Profile, Experience, Education, Skills, Languages, Projects, Blog Posts, Categories, Technologies, etc.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils import translation as dj_translation
from django.utils.text import slugify
from datetime import datetime, timedelta
from portfolio.models import (
    Profile, Project, Technology, Experience, Education, Skill, Language,
    BlogPost, Contact, Category, ProjectType
)
import random


class Command(BaseCommand):
    help = 'Pobla el portfolio con datos de prueba completos (comando unificado)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Resetear todos los datos antes de poblar (ADVERTENCIA: Eliminará datos existentes)',
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default='admin123',
            help='Contraseña para el usuario admin (default: admin123)',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(
                self.style.WARNING('⚠️  Reseteando todos los datos... ¡Esto eliminará el contenido existente!')
            )
            self.reset_data()

        self.stdout.write('🚀 Creando datos de prueba completos...')

        # Crear usuario admin
        admin_password = options['admin_password']
        admin_user = self.create_admin_user(admin_password)

        # Crear categorías primero
        categories = self.create_categories()

        # Crear tipos de proyectos
        project_types = self.create_project_types()

        # Crear tecnologías
        self.create_technologies()

        # Crear perfil
        profile = self.create_profile()

        # Crear experiencias laborales
        experiences = self.create_experiences()

        # Crear educación
        educations = self.create_educations()

        # Crear habilidades técnicas
        skills = self.create_skills()

        # Crear idiomas (NUEVO)
        languages = self.create_languages()

        # Crear proyectos
        projects = self.create_projects(project_types)

        # Crear posts de blog
        blog_posts = self.create_blog_posts(categories)

        # Crear mensajes de contacto de ejemplo
        contacts = self.create_sample_contacts()

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ ¡Datos de prueba creados exitosamente!\n'
                f'📊 Resumen:\n'
                f'   • Usuario Admin: admin (contraseña: {admin_password})\n'
                f'   • Perfil: 1 perfil completo\n'
                f'   • Experiencia: {len(experiences)} posiciones laborales\n'
                f'   • Educación: {len(educations)} entradas educativas\n'
                f'   • Habilidades: {len(skills)} habilidades técnicas\n'
                f'   • Idiomas: {len(languages)} idiomas\n'
                f'   • Proyectos: {len(projects)} proyectos de portfolio\n'
                f'   • Posts de Blog: {len(blog_posts)} artículos\n'
                f'   • Categorías: {len(categories)} categorías de blog\n'
                f'   • Contactos: {len(contacts)} mensajes de ejemplo\n'
                f'   • Tecnologías: Auto-pobladas con iconos\n\n'
                f'🌐 URLs de Acceso:\n'
                f'   • Portfolio: http://localhost:8000/\n'
                f'   • Admin Django: http://localhost:8000/admin/ (admin/{admin_password})\n'
                f'   • Dashboard: http://localhost:8000/admin-dashboard/\n'
                f'   • Analytics: http://localhost:8000/admin-analytics/\n'
            )
        )

    def reset_data(self):
        """Resetear todos los datos del portfolio"""
        models_to_reset = [Contact, BlogPost, Project, Experience, Education, Skill, Language, Profile]

        for model in models_to_reset:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(f'   Eliminados {count} registros de {model.__name__}')

    def create_admin_user(self, password):
        """Crear usuario admin si no existe"""
        if User.objects.filter(username='admin').exists():
            admin_user = User.objects.get(username='admin')
            self.stdout.write('👤 Usuario admin ya existe')
        else:
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@portfolio.com',
                password=password,
                first_name='Portfolio',
                last_name='Admin'
            )
            self.stdout.write(self.style.SUCCESS(f'👤 Usuario admin creado (contraseña: {password})'))

        return admin_user

    def create_categories(self):
        """Crear categorías de blog"""
        categories_data = [
            {
                'slug': 'desarrollo-web',
                'order': 1,
                'name': 'Web Development',
                'description': 'Articles about frontend and backend development',
            },
            {
                'slug': 'inteligencia-artificial',
                'order': 2,
                'name': 'Artificial Intelligence',
                'description': 'Content covering AI, ML and Data Science',
            },
            {
                'slug': 'devops',
                'order': 3,
                'name': 'DevOps',
                'description': 'Tools and best practices for DevOps teams',
            },
            {
                'slug': 'tutorial',
                'order': 4,
                'name': 'Tutorials',
                'description': 'Step-by-step guides and tutorials',
            },
            {
                'slug': 'opinion',
                'order': 5,
                'name': 'Opinion',
                'description': 'Technical reflections and thought leadership',
            },
        ]

        language_code = 'en'
        categories = []
        for cat_data in categories_data:
            defaults = {
                'order': cat_data['order'],
                'is_active': True,
            }
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=defaults,
            )
            with dj_translation.override(language_code):
                if created or not category.safe_translation_getter('name', language_code=language_code):
                    category.set_current_language(language_code)
                    category.name = cat_data['name']
                    category.description = cat_data['description']
                    category.save()
            categories.append(category)
            if created:
                display_name = category.safe_translation_getter('name', language_code=language_code, default=category.slug)
                self.stdout.write(f'   ✅ Categoría creada: {display_name}')

        return categories

    def create_project_types(self):
        """Crear tipos de proyectos"""
        types_data = [
            {'slug': 'web-app', 'order': 1, 'label': 'Web Application'},
            {'slug': 'api-rest', 'order': 2, 'label': 'REST API'},
            {'slug': 'mobile-app', 'order': 3, 'label': 'Mobile Application'},
            {'slug': 'dashboard', 'order': 4, 'label': 'Dashboard'},
            {'slug': 'ecommerce', 'order': 5, 'label': 'E-commerce'},
            {'slug': 'automation', 'order': 6, 'label': 'Automation'},
        ]

        language_code = 'en'
        project_types = []
        for type_data in types_data:
            defaults = {
                'order': type_data['order'],
                'is_active': True,
            }
            project_type, created = ProjectType.objects.get_or_create(
                slug=type_data['slug'],
                defaults=defaults,
            )
            with dj_translation.override(language_code):
                if created or not project_type.safe_translation_getter('name', language_code=language_code):
                    project_type.set_current_language(language_code)
                    project_type.name = type_data['label']
                    project_type.description = ''
                    project_type.save()
            project_types.append(project_type)
            if created:
                display_name = project_type.safe_translation_getter('name', language_code=language_code, default=project_type.slug)
                self.stdout.write(f'   ✅ Tipo de proyecto creado: {display_name}')

        return project_types

    def create_technologies(self):
        """Crear tecnologías de ejemplo con iconos y colores"""
        technologies_data = {
            'languages': [
                ('Python', 'fab fa-python', '#3776ab'),
                ('JavaScript', 'fab fa-js-square', '#f7df1e'),
                ('TypeScript', 'fab fa-js-square', '#3178c6'),
                ('Java', 'fab fa-java', '#ed8b00'),
                ('PHP', 'fab fa-php', '#777bb4'),
                ('Go', 'fab fa-golang', '#00add8'),
                ('Ruby', 'fas fa-gem', '#cc342d'),
            ],
            'frontend': [
                ('React', 'fab fa-react', '#61dafb'),
                ('Vue.js', 'fab fa-vuejs', '#4fc08d'),
                ('Angular', 'fab fa-angular', '#dd0031'),
                ('HTML5', 'fab fa-html5', '#e34f26'),
                ('CSS3', 'fab fa-css3-alt', '#1572b6'),
                ('Sass', 'fab fa-sass', '#cc6699'),
                ('Bootstrap', 'fab fa-bootstrap', '#7952b3'),
                ('Tailwind CSS', 'fas fa-wind', '#06b6d4'),
            ],
            'backend': [
                ('Django', 'fas fa-server', '#092e20'),
                ('Flask', 'fas fa-flask', '#000000'),
                ('Node.js', 'fab fa-node-js', '#339933'),
                ('Express.js', 'fas fa-server', '#000000'),
                ('Laravel', 'fab fa-laravel', '#ff2d20'),
                ('FastAPI', 'fas fa-rocket', '#009688'),
            ],
            'databases': [
                ('PostgreSQL', 'fas fa-database', '#336791'),
                ('MySQL', 'fas fa-database', '#4479a1'),
                ('MongoDB', 'fas fa-database', '#47a248'),
                ('Redis', 'fas fa-database', '#dc382d'),
            ],
            'devops': [
                ('Docker', 'fab fa-docker', '#2496ed'),
                ('Kubernetes', 'fas fa-dharmachakra', '#326ce5'),
                ('AWS', 'fab fa-aws', '#ff9900'),
                ('Git', 'fab fa-git-alt', '#f05032'),
                ('GitHub', 'fab fa-github', '#181717'),
            ],
        }

        language_code = 'en'
        created_count = 0
        for category, techs in technologies_data.items():
            for index, (name, icon, color) in enumerate(techs, start=1):
                identifier = slugify(name) or f"{category}-{index}"
                tech, created = Technology.objects.get_or_create(
                    identifier=identifier,
                    defaults={'icon': icon, 'color': color},
                )
                with dj_translation.override(language_code):
                    if created or not tech.safe_translation_getter('name', language_code=language_code):
                        tech.set_current_language(language_code)
                        tech.name = name
                if tech.icon != icon or tech.color != color or created:
                    tech.icon = icon
                    tech.color = color
                    tech.save()
                if created:
                    created_count += 1

        if created_count > 0:
            self.stdout.write(f'⚙️ {created_count} tecnologías creadas con iconos y colores')
        else:
            self.stdout.write('ℹ️ Tecnologías ya existen')

    def create_profile(self):
        """Crear perfil de ejemplo"""
        if Profile.objects.exists():
            profile = Profile.objects.first()
            self.stdout.write('👤 Perfil ya existe, actualizando...')
        else:
            profile = Profile.objects.create()
            self.stdout.write('👤 Nuevo perfil creado')

        # Actualizar perfil con datos de ejemplo
        profile.name = "Alex Developer"
        profile.title = "Full Stack Developer & Tech Lead"
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
        profile.save()

        return profile

    def create_experiences(self):
        """Crear experiencias laborales de ejemplo"""
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
                self.stdout.write(f'   💼 Experiencia creada: {experience.job_title} en {experience.company}')

        return experiences

    def create_educations(self):
        """Crear entradas de educación de ejemplo"""
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
                self.stdout.write(f'   🎓 Educación creada: {education.degree} de {education.institution}')

        return educations

    def create_skills(self):
        """Crear habilidades técnicas de ejemplo"""
        skills_data = [
            # Lenguajes de Programación
            {'name': 'Python', 'proficiency': 'expert', 'years_experience': 5, 'category': 'languages', 'order': 1},
            {'name': 'JavaScript', 'proficiency': 'expert', 'years_experience': 4, 'category': 'languages', 'order': 2},
            {'name': 'TypeScript', 'proficiency': 'advanced', 'years_experience': 2, 'category': 'languages', 'order': 3},

            # Frontend
            {'name': 'React', 'proficiency': 'expert', 'years_experience': 4, 'category': 'frontend', 'order': 4},
            {'name': 'Vue.js', 'proficiency': 'advanced', 'years_experience': 2, 'category': 'frontend', 'order': 5},
            {'name': 'HTML5', 'proficiency': 'expert', 'years_experience': 5, 'category': 'frontend', 'order': 6},
            {'name': 'CSS3', 'proficiency': 'expert', 'years_experience': 5, 'category': 'frontend', 'order': 7},

            # Backend
            {'name': 'Django', 'proficiency': 'expert', 'years_experience': 5, 'category': 'backend', 'order': 8},
            {'name': 'FastAPI', 'proficiency': 'advanced', 'years_experience': 2, 'category': 'backend', 'order': 9},
            {'name': 'Node.js', 'proficiency': 'advanced', 'years_experience': 3, 'category': 'backend', 'order': 10},

            # Bases de Datos
            {'name': 'PostgreSQL', 'proficiency': 'expert', 'years_experience': 4, 'category': 'databases', 'order': 11},
            {'name': 'MongoDB', 'proficiency': 'advanced', 'years_experience': 3, 'category': 'databases', 'order': 12},
            {'name': 'Redis', 'proficiency': 'intermediate', 'years_experience': 2, 'category': 'databases', 'order': 13},

            # DevOps
            {'name': 'Docker', 'proficiency': 'advanced', 'years_experience': 3, 'category': 'devops', 'order': 14},
            {'name': 'AWS', 'proficiency': 'advanced', 'years_experience': 3, 'category': 'devops', 'order': 15},
            {'name': 'Git', 'proficiency': 'expert', 'years_experience': 5, 'category': 'devops', 'order': 16},
        ]

        skills = []
        for skill_data in skills_data:
            skill, created = Skill.objects.get_or_create(
                name=skill_data['name'],
                defaults=skill_data
            )
            skills.append(skill)
            if created:
                self.stdout.write(f'   ⚡ Habilidad creada: {skill.name} ({skill.proficiency})')

        return skills

    def create_languages(self):
        """Crear idiomas hablados de ejemplo"""
        languages_data = [
            {'code': 'en', 'label': 'English', 'proficiency': 'Native', 'order': 1},
            {'code': 'es', 'label': 'Spanish', 'proficiency': 'C2', 'order': 2},
            {'code': 'fr', 'label': 'French', 'proficiency': 'B2', 'order': 3},
            {'code': 'de', 'label': 'German', 'proficiency': 'A2', 'order': 4},
        ]

        language_code = 'en'
        languages = []
        for lang_data in languages_data:
            defaults = {
                'proficiency': lang_data['proficiency'],
                'order': lang_data['order'],
            }
            language, created = Language.objects.get_or_create(
                code=lang_data['code'],
                defaults=defaults,
            )
            with dj_translation.override(language_code):
                if created or not language.safe_translation_getter('name', language_code=language_code):
                    language.set_current_language(language_code)
                    language.name = lang_data['label']
                    language.save()
            languages.append(language)
            if created:
                display_name = language.safe_translation_getter('name', language_code=language_code, default=language.code)
                self.stdout.write(f'   🌍 Idioma creado: {display_name} ({language.proficiency})')

        return languages

    def create_projects(self, project_types):
        """Crear proyectos de ejemplo"""
        technologies = list(Technology.objects.all()[:20])

        projects_data = [
            {
                'title': 'E-commerce Platform Advanced',
                'description': 'Plataforma completa de e-commerce con panel de administración, sistema de pagos, inventario y analytics en tiempo real.',
                'detailed_description': """**E-commerce Platform Advanced** es una solución completa de comercio electrónico desarrollada desde cero con tecnologías modernas.

### Características Principales:
- Frontend Responsivo con React y Tailwind CSS
- Backend Robusto con Django y Django REST Framework
- Pagos Seguros con Stripe y PayPal
- Gestión de Inventario completa
- Panel de Administración con métricas en tiempo real

### Resultados:
- +500k usuarios registrados en el primer año
- 99.9% uptime con arquitectura cloud escalable
- 40% mejora en conversión vs plataforma anterior""",
                'github_url': 'https://github.com/alex-developer/ecommerce-advanced',
                'demo_url': 'https://ecommerce-demo.alexdev.com',
                'project_type': project_types[4] if len(project_types) > 4 else None,
                'featured': True,
                'order': 1,
                'visibility': 'public'
            },
            {
                'title': 'Analytics Dashboard Pro',
                'description': 'Dashboard interactivo para visualización de datos empresariales con gráficos en tiempo real y reportes automatizados.',
                'detailed_description': """**Analytics Dashboard Pro** transforma datos complejos en insights accionables.

### Funcionalidades:
- Visualizaciones Dinámicas con Chart.js
- Tiempo Real con WebSockets
- Reportes Automatizados en PDF
- Multi-tenant

### Impacto:
- 60% reducción en tiempo de análisis
- +15 empresas utilizando la plataforma""",
                'github_url': 'https://github.com/alex-developer/analytics-dashboard',
                'demo_url': 'https://analytics.alexdev.com',
                'project_type': project_types[3] if len(project_types) > 3 else None,
                'featured': True,
                'order': 2,
                'visibility': 'public'
            },
            {
                'title': 'API REST Microservices',
                'description': 'Arquitectura de microservicios escalable con autenticación JWT, rate limiting y documentación automática.',
                'detailed_description': """**API REST Microservices** es una arquitectura robusta diseñada para aplicaciones empresariales.

### Arquitectura:
- Microservicios independientes
- API Gateway con Kong
- Autenticación JWT
- Documentación Swagger automática

### Métricas:
- <100ms latencia promedio
- 10k+ requests/minuto soportados""",
                'github_url': 'https://github.com/alex-developer/api-microservices',
                'demo_url': 'https://api.alexdev.com/docs',
                'project_type': project_types[1] if len(project_types) > 1 else None,
                'featured': True,
                'order': 3,
                'visibility': 'public'
            },
        ]

        projects = []
        for proj_data in projects_data:
            project, created = Project.objects.get_or_create(
                title=proj_data['title'],
                defaults=proj_data
            )

            if created and technologies:
                project_techs = random.sample(technologies, min(6, len(technologies)))
                project.technologies.set(project_techs)

            projects.append(project)
            if created:
                self.stdout.write(f'   🚀 Proyecto creado: {project.title}')

        return projects

    def create_blog_posts(self, categories):
        """Crear posts de blog de ejemplo"""
        blog_posts_data = [
            {
                'title': 'Construyendo APIs Escalables con Django REST Framework',
                'slug': 'apis-escalables-django-rest-framework',
                'excerpt': 'Guía completa para desarrollar APIs REST robustas y escalables usando Django REST Framework.',
                'content': """# Construyendo APIs Escalables con Django REST Framework

Django REST Framework (DRF) ha revolucionado la forma en que desarrollamos APIs en Python.

## ¿Por qué Django REST Framework?

- Serialización robusta
- Autenticación integrada
- Documentación automática
- Viewsets y Routers

## Mejores Prácticas

1. Usa viewsets para reducir código
2. Implementa paginación
3. Añade throttling para rate limiting
4. Documenta con Swagger

## Conclusión

DRF es una herramienta poderosa para crear APIs profesionales.""",
                'category': categories[0] if categories else None,
                'published': True,
                'featured': True,
                'views_count': random.randint(100, 500),
            },
            {
                'title': 'Introducción a Docker para Desarrolladores',
                'slug': 'introduccion-docker-desarrolladores',
                'excerpt': 'Aprende los fundamentos de Docker y cómo puede mejorar tu flujo de trabajo de desarrollo.',
                'content': """# Introducción a Docker para Desarrolladores

Docker ha transformado la forma en que desarrollamos y desplegamos aplicaciones.

## ¿Qué es Docker?

Docker es una plataforma de contenedores que permite empaquetar aplicaciones con todas sus dependencias.

## Ventajas

- Consistencia entre entornos
- Aislamiento de aplicaciones
- Fácil escalabilidad
- Despliegue rápido

## Primeros Pasos

```bash
docker run hello-world
docker build -t myapp .
docker-compose up
```

## Conclusión

Docker es esencial en el desarrollo moderno.""",
                'category': categories[2] if len(categories) > 2 else None,
                'published': True,
                'featured': False,
                'views_count': random.randint(50, 300),
            },
        ]

        blog_posts = []
        for post_data in blog_posts_data:
            blog_post, created = BlogPost.objects.get_or_create(
                slug=post_data['slug'],
                defaults=post_data
            )
            blog_posts.append(blog_post)
            if created:
                self.stdout.write(f'   📝 Post de blog creado: {blog_post.title}')

        return blog_posts

    def create_sample_contacts(self):
        """Crear mensajes de contacto de ejemplo"""
        contacts_data = [
            {
                'name': 'John Smith',
                'email': 'john.smith@example.com',
                'subject': 'Consulta sobre proyecto web',
                'message': 'Hola, estoy interesado en contratar tus servicios para desarrollar una aplicación web. ¿Podríamos agendar una llamada?',
                'status': 'new'
            },
            {
                'name': 'María García',
                'email': 'maria.garcia@example.com',
                'subject': 'Colaboración en proyecto open source',
                'message': 'Me encantó tu trabajo en GitHub. ¿Te gustaría colaborar en un proyecto open source?',
                'status': 'read'
            },
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
                self.stdout.write(f'   📧 Contacto creado: {contact.name}')

        return contacts
