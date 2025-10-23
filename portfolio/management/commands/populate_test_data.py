"""
Populate the portfolio database with a rich multilingual demo dataset.

Creates:
- Admin user (username: admin)
- Profile with John Doe persona
- Experiences, education entries, skills, and language proficiency
- Knowledge bases, project types, categories
- 12 showcase projects with knowledge base links
- 10 blog posts with English and Spanish content
- Sample contacts
"""

from datetime import date, timedelta
from textwrap import dedent

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils import translation as dj_translation

from portfolio.models import (
    BlogPost,
    Category,
    Contact,
    Education,
    Experience,
    KnowledgeBase,
    Language,
    Profile,
    Project,
    ProjectType,
    Skill,
)


class Command(BaseCommand):
    help = "Populate the portfolio with a complete multilingual demo dataset."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing demo data before seeding.",
        )
        parser.add_argument(
            "--admin-password",
            type=str,
            default="admin123",
            help="Password for the generated admin user (default: admin123).",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write(self.style.WARNING("Resetting existing portfolio data..."))
            self.reset_data()

        admin_password = options["admin_password"]
        self.ensure_admin_user(admin_password)

        categories = self.create_categories()
        blog_posts = self.create_blog_posts(categories)
        project_types = self.create_project_types()
        knowledge_bases = self.create_knowledge_bases()
        profile = self.create_profile()
        experiences = self.create_experiences()
        educations = self.create_educations()
        skills = self.create_skills()
        languages = self.create_languages()
        projects = self.create_projects(project_types, knowledge_bases, blog_posts)
        contacts = self.create_contacts()

        summary = dedent(
            f"""
            Demo data created successfully!

            Counts
              - Profile: {1 if profile else 0}
              - Experiences: {len(experiences)}
              - Education entries: {len(educations)}
              - Skills: {len(skills)}
              - Languages: {len(languages)}
              - Knowledge bases: {len(knowledge_bases)}
              - Project types: {len(project_types)}
              - Projects: {len(projects)}
              - Blog posts: {len(blog_posts)}
              - Categories: {len(categories)}
              - Contacts: {len(contacts)}

            Access
              - Portfolio: http://localhost:8000/
              - Dashboard: http://localhost:8000/admin-dashboard/
              - Admin (Django): http://localhost:8000/admin/  (admin / {admin_password})
            """
        ).strip()
        self.stdout.write(self.style.SUCCESS(summary))

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def reset_data(self):
        """Delete demo content so the seed is deterministic."""
        models_to_clear = [
            BlogPost,
            Project,
            Experience,
            Education,
            Skill,
            Language,
            KnowledgeBase,
            Category,
            ProjectType,
            Contact,
        ]
        for model in models_to_clear:
            deleted = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(f"  Cleared {deleted} rows from {model.__name__}")
        Profile.objects.all().delete()
        self.stdout.write("  Cleared profile records")

    def ensure_admin_user(self, password):
        """Create or update the admin user with a known password."""
        User = get_user_model()
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "is_superuser": True,
                "is_staff": True,
                "first_name": "John",
                "last_name": "Doe",
            },
        )
        admin.is_superuser = True
        admin.is_staff = True
        admin.first_name = admin.first_name or "John"
        admin.last_name = admin.last_name or "Doe"
        admin.set_password(password)
        admin.save()
        if created:
            self.stdout.write(self.style.SUCCESS("  Admin user created (admin)"))
        else:
            self.stdout.write("  Admin user updated (admin)")

    def assign_translations(self, instance, translations):
        """Persist translations for a TranslatableModel instance."""
        original_language = dj_translation.get_language() or settings.LANGUAGE_CODE
        for lang_code, fields in translations.items():
            dj_translation.activate(lang_code)
            instance.set_current_language(lang_code)
            for field_name, value in fields.items():
                setattr(instance, field_name, value)
            instance.save()
        dj_translation.activate(original_language)
        instance.set_current_language(original_language)
        return instance
    # ------------------------------------------------------------------ #
    # Profile and CV content
    # ------------------------------------------------------------------ #

    def create_profile(self):
        profile = Profile.get_solo()

        profile.email = "contact@johndoe.energy"
        profile.phone = "+1 809 555 1234"
        profile.linkedin_url = "https://www.linkedin.com/in/john-doe-energy"
        profile.github_url = "https://github.com/johndoe-energy"
        profile.medium_url = "https://medium.com/@john-doe-energy"
        profile.show_web_resume = True

        translations = {
            "en": {
                "name": "John Doe",
                "title": "Senior Energy Systems Engineer",
                "bio": dedent(
                    """
                    I help utilities and clean-tech teams build software that keeps the lights on.
                    During the last decade I have designed battery storage controllers, microgrid optimisers,
                    and the dashboards that operators rely on every day.

                    My work blends electrical engineering, data science, and product strategy.
                    I enjoy mentoring teams, writing about technology, and experimenting with new ways
                    to tell the story of clean energy.
                    """
                ).strip(),
                "location": "Santo Domingo, Dominican Republic",
            },
            "es": {
                "name": "John Doe",
                "title": "Ingeniero Senior de Sistemas de Energia",
                "bio": dedent(
                    """
                    Ayudo a empresas de energia y equipos de tecnologia limpia a crear software
                    que mantiene la red operando. Durante la ultima decada he disenado controladores
                    para almacenamiento en baterias, optimizadores de microredes y tableros de operacion.

                    Mi trabajo combina ingenieria electrica, ciencia de datos y estrategia de producto.
                    Disfruto acompanando equipos, escribir sobre tecnologia y contar historias sobre energia limpia.
                    """
                ).strip(),
                "location": "Santo Domingo, Republica Dominicana",
            },
        }
        self.assign_translations(profile, translations)
        self.stdout.write("  Profile updated for John Doe")
        return profile

    def create_experiences(self):
        experiences_data = [
            {
                "order": 1,
                "start": date(2021, 5, 1),
                "end": None,
                "current": True,
                "translations": {
                    "en": {
                        "company": "Solara Gridworks",
                        "position": "Principal Energy Systems Engineer",
                        "description": dedent(
                            """
                            Lead the engineering team delivering microgrid control software to island utilities.
                            - Architected a modular edge platform that synchronises with the cloud every five minutes.
                            - Coordinated commissioning of four battery energy storage systems totalling 48 MWh.
                            - Partner with field crews to transform telemetry into operating playbooks.
                            """
                        ).strip(),
                    },
                    "es": {
                        "company": "Solara Gridworks",
                        "position": "Ingeniero Principal de Sistemas de Energia",
                        "description": dedent(
                            """
                            Lidero el equipo que desarrolla software de control para microredes en islas.
                            - Disene una plataforma modular que sincroniza datos cada cinco minutos.
                            - Coordine la puesta en marcha de cuatro sistemas de baterias con 48 MWh.
                            - Trabajo con los equipos de campo para convertir telemetria en guias operativas.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "order": 2,
                "start": date(2018, 2, 1),
                "end": date(2021, 3, 1),
                "current": False,
                "translations": {
                    "en": {
                        "company": "Nova Energy Cooperative",
                        "position": "Digital Innovation Manager",
                        "description": dedent(
                            """
                            Delivered the cooperative-wide roadmap for analytics and automation.
                            Built the first predictive maintenance models for the wind fleet,
                            reducing unplanned downtime by fourteen percent. Introduced design sprints
                            to align engineers, analysts, and operators.
                            """
                        ).strip(),
                    },
                    "es": {
                        "company": "Nova Energy Cooperative",
                        "position": "Gerente de Innovacion Digital",
                        "description": dedent(
                            """
                            Defini la hoja de ruta de analitica y automatizacion para la cooperativa.
                            Cree los primeros modelos de mantenimiento predictivo para el parque eolico,
                            reduciendo paradas no planificadas en catorce por ciento. Introduje design sprints
                            para alinear ingenieros, analistas y operadores.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "order": 3,
                "start": date(2015, 6, 1),
                "end": date(2018, 1, 1),
                "current": False,
                "translations": {
                    "en": {
                        "company": "BrightFuture Labs",
                        "position": "Lead Software Engineer",
                        "description": dedent(
                            """
                            Built data pipelines and web applications for sustainability startups.
                            Mentored developers on Django and React best practices and instituted
                            continuous delivery pipelines that shrank release cycles from weeks to days.
                            """
                        ).strip(),
                    },
                    "es": {
                        "company": "BrightFuture Labs",
                        "position": "Ingeniero Lider de Software",
                        "description": dedent(
                            """
                            Cree tuberias de datos y aplicaciones web para startups de sostenibilidad.
                            Guie a los desarrolladores en buenas practicas con Django y React e
                            implemente canalizaciones de entrega continua que redujeron los lanzamientos
                            de semanas a dias.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "order": 4,
                "start": date(2012, 1, 1),
                "end": date(2015, 5, 1),
                "current": False,
                "translations": {
                    "en": {
                        "company": "GreenSpark Consulting",
                        "position": "Energy Analyst",
                        "description": dedent(
                            """
                            Modelled renewable portfolios and advised on battery storage investments.
                            Delivered decision briefings for executive boards and authored technical papers
                            on microgrid economics.
                            """
                        ).strip(),
                    },
                    "es": {
                        "company": "GreenSpark Consulting",
                        "position": "Analista de Energia",
                        "description": dedent(
                            """
                            Modele carteras de energias renovables y asesore sobre inversiones en baterias.
                            Prepare informes ejecutivos y publique articulos tecnicos sobre economia de microredes.
                            """
                        ).strip(),
                    },
                },
            },
        ]

        experiences = []
        for data in experiences_data:
            defaults = {
                "start_date": data["start"],
                "end_date": data["end"],
                "current": data["current"],
                "order": data["order"],
            }
            experience, _ = Experience.objects.update_or_create(
                order=data["order"],
                defaults=defaults,
            )
            self.assign_translations(experience, data["translations"])
            experiences.append(experience)
        self.stdout.write(f"  Created/updated {len(experiences)} experiences")
        return experiences

    def create_educations(self):
        educations_data = [
            {
                "order": 1,
                "education_type": "formal",
                "start": date(2010, 9, 1),
                "end": date(2012, 6, 1),
                "current": False,
                "credential_id": "",
                "credential_url": "",
                "translations": {
                    "en": {
                        "institution": "Massachusetts Institute of Technology",
                        "degree": "MSc in Sustainable Energy Engineering",
                        "field_of_study": "Energy Systems",
                        "description": "Thesis on optimisation strategies for island microgrids with high renewable penetration.",
                    },
                    "es": {
                        "institution": "Massachusetts Institute of Technology",
                        "degree": "Maestria en Ingenieria de Energia Sostenible",
                        "field_of_study": "Sistemas de Energia",
                        "description": "Tesis sobre estrategias de optimizacion para microredes insulares con alta penetracion renovable.",
                    },
                },
            },
            {
                "order": 2,
                "education_type": "formal",
                "start": date(2006, 9, 1),
                "end": date(2010, 6, 1),
                "current": False,
                "credential_id": "",
                "credential_url": "",
                "translations": {
                    "en": {
                        "institution": "Universidad Politecnica de Madrid",
                        "degree": "BEng in Electrical Engineering",
                        "field_of_study": "Power Systems",
                        "description": "Capstone project on distributed generation integration for rural communities.",
                    },
                    "es": {
                        "institution": "Universidad Politecnica de Madrid",
                        "degree": "Ingenieria en Electricidad",
                        "field_of_study": "Sistemas Electricos",
                        "description": "Proyecto final sobre integracion de generacion distribuida para comunidades rurales.",
                    },
                },
            },
            {
                "order": 3,
                "education_type": "certification",
                "start": date(2019, 1, 1),
                "end": date(2019, 6, 1),
                "current": False,
                "credential_id": "MLENG-2019-445",
                "credential_url": "https://online.stanford.edu/certificates/machine-learning",
                "translations": {
                    "en": {
                        "institution": "Stanford Online",
                        "degree": "Certificate in Machine Learning",
                        "field_of_study": "Applied Machine Learning",
                        "description": "Focused on forecasting models for energy demand and equipment health.",
                    },
                    "es": {
                        "institution": "Stanford Online",
                        "degree": "Certificado en Machine Learning",
                        "field_of_study": "Aprendizaje Automatico Aplicado",
                        "description": "Enfoque en pronosticos de demanda de energia y salud de activos.",
                    },
                },
            },
        ]

        educations = []
        for data in educations_data:
            defaults = {
                "education_type": data["education_type"],
                "start_date": data["start"],
                "end_date": data["end"],
                "current": data["current"],
                "credential_id": data["credential_id"],
                "credential_url": data["credential_url"],
                "order": data["order"],
            }
            education, _ = Education.objects.update_or_create(
                order=data["order"],
                defaults=defaults,
            )
            self.assign_translations(education, data["translations"])
            educations.append(education)
        self.stdout.write(f"  Created/updated {len(educations)} education entries")
        return educations
    # ------------------------------------------------------------------ #
    # Skills, languages, categories
    # ------------------------------------------------------------------ #

    def create_skills(self):
        skills_data = [
            ("Python", "Programming", 4, 10),
            ("Django and FastAPI", "Programming", 4, 9),
            ("React", "Frontend", 3, 7),
            ("Docker and Kubernetes", "Cloud and DevOps", 3, 6),
            ("AWS Architecture", "Cloud and DevOps", 3, 5),
            ("Data Modelling", "Data and Analytics", 4, 9),
            ("Machine Learning", "Data and Analytics", 3, 6),
            ("Business Storytelling", "Leadership", 4, 8),
            ("Energy Market Design", "Energy Systems", 3, 7),
            ("Microgrid Planning", "Energy Systems", 4, 8),
            ("Product Discovery", "Product", 4, 7),
            ("Design Sprints", "Product", 3, 6),
        ]

        skills = []
        for name, category, proficiency, years in skills_data:
            skill = (
                Skill.objects.language("en")
                .filter(translations__name__iexact=name)
                .first()
            )
            if not skill:
                skill = Skill()
            skill.category = category
            skill.proficiency = proficiency
            skill.years_experience = years
            skill.save()
            translations = {"en": {"name": name}, "es": {"name": name}}
            self.assign_translations(skill, translations)
            skills.append(skill)
        self.stdout.write(f"  Created/updated {len(skills)} skills")
        return skills

    def create_languages(self):
        languages_data = [
            ("en", "English", "Native", 1, "Ingles"),
            ("es", "Spanish", "C1", 2, "Espanol"),
            ("fr", "French", "B1", 3, "Frances"),
        ]
        language_objects = []
        for code, name_en, proficiency, order, name_es in languages_data:
            language, _ = Language.objects.update_or_create(
                code=code,
                defaults={"proficiency": proficiency, "order": order},
            )
            translations = {"en": {"name": name_en}, "es": {"name": name_es}}
            self.assign_translations(language, translations)
            language_objects.append(language)
        self.stdout.write(f"  Created/updated {len(language_objects)} languages")
        return language_objects

    def create_categories(self):
        categories_data = [
            (
                "software-architecture",
                1,
                "Software Architecture",
                "Arquitectura de Software",
                "Patterns, tooling, and leadership for maintainable platforms.",
                "Patrones, herramientas y liderazgo para plataformas mantenibles.",
            ),
            (
                "renewable-energy",
                2,
                "Renewable Energy Systems",
                "Sistemas de Energia Renovable",
                "Design notes for solar, wind, storage, and microgrids.",
                "Notas de diseno para solar, eolica, almacenamiento y microredes.",
            ),
            (
                "sustainability",
                3,
                "Sustainability and Strategy",
                "Sostenibilidad y Estrategia",
                "Frameworks that connect net-zero targets with daily decisions.",
                "Marcos que conectan objetivos net zero con decisiones diarias.",
            ),
            (
                "data-science",
                4,
                "Data Science and AI",
                "Ciencia de Datos e IA",
                "Forecasting, anomaly detection, and applied machine learning.",
                "Pronosticos, deteccion de anomalias y machine learning aplicado.",
            ),
            (
                "product-reviews",
                5,
                "Product Reviews",
                "Resenas de Productos",
                "Opinions on tools that accelerate energy innovation.",
                "Opiniones sobre herramientas que aceleran la innovacion energetica.",
            ),
            (
                "career-notes",
                6,
                "Career Notes",
                "Notas de Carrera",
                "Reflections from field work and mentoring in the energy sector.",
                "Reflexiones de trabajo en campo y mentoria en el sector energia.",
            ),
            (
                "tutorials",
                7,
                "Hands-on Tutorials",
                "Tutoriales Practicos",
                "Step by step guides for building energy and analytics tools.",
                "Guias paso a paso para construir herramientas de energia y analitica.",
            ),
        ]

        categories = {}
        for slug, order, name_en, name_es, desc_en, desc_es in categories_data:
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"order": order, "is_active": True},
            )
            translations = {
                "en": {"name": name_en, "description": desc_en},
                "es": {"name": name_es, "description": desc_es},
            }
            self.assign_translations(category, translations)
            categories[slug] = category
        self.stdout.write(f"  Created/updated {len(categories)} categories")
        return categories
    def create_project_types(self):
        types_data = [
            (
                "energy-platforms",
                1,
                "Energy Platforms",
                "Plataformas de Energia",
                "Digital products that run renewable infrastructure.",
                "Productos digitales que operan infraestructura renovable.",
            ),
            (
                "analytics-solutions",
                2,
                "Analytics Solutions",
                "Soluciones de Analitica",
                "Data products that support forecasting and operations.",
                "Productos de datos para pronosticos y operaciones.",
            ),
            (
                "research-initiative",
                3,
                "Research Initiatives",
                "Iniciativas de Investigacion",
                "Exploratory projects that test ideas with partners.",
                "Proyectos exploratorios para probar ideas con socios.",
            ),
            (
                "product-experiences",
                4,
                "Product Experiences",
                "Experiencias de Producto",
                "Apps and sites that communicate complex energy stories.",
                "Aplicaciones y sitios que comunican historias de energia complejas.",
            ),
            (
                "consulting-engagement",
                5,
                "Consulting Engagements",
                "Proyectos de Consultoria",
                "Short engagements focused on roadmaps and capability building.",
                "Proyectos cortos enfocados en hojas de ruta y desarrollo de capacidades.",
            ),
        ]

        project_types = {}
        for slug, order, name_en, name_es, desc_en, desc_es in types_data:
            project_type, _ = ProjectType.objects.update_or_create(
                slug=slug,
                defaults={"order": order, "is_active": True},
            )
            translations = {
                "en": {"name": name_en, "description": desc_en},
                "es": {"name": name_es, "description": desc_es},
            }
            self.assign_translations(project_type, translations)
            project_types[slug] = project_type
        self.stdout.write(f"  Created/updated {len(project_types)} project types")
        return project_types

    def create_knowledge_bases(self):
        knowledge_data = [
            ("python", "Python", "Python", "fab fa-python", "#3776AB"),
            ("django", "Django", "Django", "fas fa-server", "#092E20"),
            ("react", "React", "React", "fab fa-react", "#61DAFB"),
            ("docker", "Docker", "Docker", "fab fa-docker", "#2496ED"),
            ("aws", "Amazon Web Services", "Amazon Web Services", "fab fa-aws", "#FF9900"),
            ("postgresql", "PostgreSQL", "PostgreSQL", "fas fa-database", "#336791"),
            ("kubernetes", "Kubernetes", "Kubernetes", "fas fa-dharmachakra", "#326CE5"),
            ("bess", "Battery Energy Storage", "Almacenamiento de Energia en Baterias", "fas fa-battery-full", "#4CAF50"),
            ("microgrids", "Microgrid Planning", "Planificacion de Microredes", "fas fa-plug", "#4A90E2"),
            ("sustainability", "Sustainability Strategy", "Estrategia de Sostenibilidad", "fas fa-leaf", "#2ECC71"),
            ("data-analytics", "Data Analytics", "Analitica de Datos", "fas fa-chart-line", "#8E44AD"),
            ("machine-learning", "Machine Learning", "Aprendizaje Automatico", "fas fa-brain", "#F39C12"),
            ("design-thinking", "Design Thinking", "Design Thinking", "fas fa-lightbulb", "#E67E22"),
            ("edge-computing", "Edge Computing", "Edge Computing", "fas fa-network-wired", "#2C3E50"),
            ("power-bi", "Power BI", "Power BI", "fas fa-chart-pie", "#F2C811"),
        ]

        knowledge = {}
        for identifier, name_en, name_es, icon, color in knowledge_data:
            kb, _ = KnowledgeBase.objects.update_or_create(
                identifier=identifier,
                defaults={"icon": icon, "color": color},
            )
            translations = {"en": {"name": name_en}, "es": {"name": name_es}}
            self.assign_translations(kb, translations)
            knowledge[identifier] = kb
        self.stdout.write(f"  Created/updated {len(knowledge)} knowledge bases")
        return knowledge
    def create_projects(self, project_types, knowledge_bases, blog_posts):
        projects_data = [
            {
                "slug": "smart-solar-operations-console",
                "project_type_slug": "energy-platforms",
                "project_type_choice": "implementation",
                "order": 10,
                "featured": True,
                "primary_language": "Python",
                "stars": 126,
                "forks": 18,
                "knowledge_ids": ["microgrids", "python", "django", "react", "aws", "data-analytics"],
                "demo_url": "https://demo.johndoe.energy/solara-console",
                "translations": {
                    "en": {
                        "title": "Smart Solar Operations Console",
                        "description": "A dashboard that gives island utilities real-time control of solar and battery assets.",
                        "detailed_description": dedent(
                            """
                            Designed and delivered a responsive console that fuses edge telemetry, forecasting,
                            and human-friendly workflows. Operators can rehearse contingencies, push firmware
                            updates, and receive explainable AI recommendations on how to dispatch storage assets.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Consola Inteligente de Operaciones Solares",
                        "description": "Tablero para que las empresas electricas gestionen solar y baterias en tiempo real.",
                        "detailed_description": dedent(
                            """
                            Disenamos una consola adaptable que combina telemetria, pronosticos y flujos amigables.
                            Los operadores ensayan contingencias, publican firmware y reciben recomendaciones
                            explicables sobre como despachar el almacenamiento.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "slug": "bess-optimizer-suite",
                "project_type_slug": "analytics-solutions",
                "project_type_choice": "api",
                "order": 20,
                "featured": True,
                "primary_language": "Python",
                "stars": 214,
                "forks": 42,
                "knowledge_ids": ["bess", "python", "machine-learning", "data-analytics", "power-bi"],
                "github_url": "https://github.com/johndoe-energy/bess-optimizer",
                "translations": {
                    "en": {
                        "title": "BESS Optimiser Suite",
                        "description": "APIs and notebooks that schedule charge and discharge cycles for large batteries.",
                        "detailed_description": dedent(
                            """
                            Developed a library of optimisation routines that evaluates price signals, weather forecasts,
                            and asset constraints. The suite includes a REST API, batch jobs, and interactive notebooks
                            that operators use to compare day-ahead strategies.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Suite de Optimizacion BESS",
                        "description": "APIs y notebooks para programar ciclos de carga y descarga de baterias industriales.",
                        "detailed_description": dedent(
                            """
                            Construimos rutinas de optimizacion que consideran precios, clima y restricciones del activo.
                            La suite incluye una API REST, trabajos batch y notebooks para comparar estrategias del dia siguiente.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "slug": "predictive-maintenance-lab",
                "project_type_slug": "analytics-solutions",
                "project_type_choice": "process",
                "order": 30,
                "featured": False,
                "primary_language": "Python",
                "stars": 165,
                "forks": 31,
                "knowledge_ids": ["machine-learning", "python", "django", "postgresql", "aws"],
                "translations": {
                    "en": {
                        "title": "Predictive Maintenance Lab",
                        "description": "A sandbox that surfaces sensor anomalies for wind and solar fleets.",
                        "detailed_description": dedent(
                            """
                            Implemented streaming feature stores, outlier detection models, and signal labelling tools.
                            The lab shortens the time between an alarm appearing and a technician understanding the root cause.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Laboratorio de Mantenimiento Predictivo",
                        "description": "Sandbox que detecta anomalias en flotas eolicas y solares.",
                        "detailed_description": dedent(
                            """
                            Implementamos feature stores, modelos de deteccion de outliers y herramientas de etiquetado.
                            El laboratorio reduce el tiempo entre una alarma y el entendimiento del problema por parte del tecnico.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "slug": "city-mobility-energy-dashboard",
                "project_type_slug": "product-experiences",
                "project_type_choice": "website",
                "order": 40,
                "featured": False,
                "primary_language": "TypeScript",
                "stars": 98,
                "forks": 12,
                "knowledge_ids": ["react", "data-analytics", "design-thinking", "sustainability"],
                "demo_url": "https://demo.johndoe.energy/mobility",
                "translations": {
                    "en": {
                        "title": "City Mobility Energy Dashboard",
                        "description": "Interactive storytelling on how public transport electrification impacts the grid.",
                        "detailed_description": dedent(
                            """
                            Combined open data, utility records, and citizen stories into an immersive dashboard.
                            Designed for city councils evaluating charging infrastructure rollouts and financing needs.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Dashboard de Movilidad Urbana",
                        "description": "Narrativa interactiva sobre el impacto de electrificar el transporte publico.",
                        "detailed_description": dedent(
                            """
                            Combinamos datos abiertos, registros de la red e historias de ciudadanos en un tablero inmersivo.
                            Dirigido a municipios que evaluan despliegues de cargadores y necesidades de financiamiento.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "slug": "hydrogen-scenario-planner",
                "project_type_slug": "research-initiative",
                "project_type_choice": "research",
                "order": 50,
                "featured": False,
                "primary_language": "Python",
                "stars": 72,
                "forks": 9,
                "knowledge_ids": ["sustainability", "data-analytics", "machine-learning"],
                "translations": {
                    "en": {
                        "title": "Hydrogen Scenario Planner",
                        "description": "Exploratory toolkit to test the economics of green hydrogen pilots.",
                        "detailed_description": dedent(
                            """
                            Built simulation models that evaluate electrolyser sizing, storage layouts, and off-take agreements.
                            The planner helps executives compare investment options with transparent assumptions.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Planificador de Escenarios de Hidrogeno",
                        "description": "Kit exploratorio para evaluar la economia de proyectos de hidrogeno verde.",
                        "detailed_description": dedent(
                            """
                            Modelamos tamano de electrolizadores, configuraciones de almacenamiento y contratos de compra.
                            El planificador permite comparar inversiones con supuestos transparentes.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "slug": "virtual-power-plant-simulator",
                "project_type_slug": "energy-platforms",
                "project_type_choice": "framework",
                "order": 60,
                "featured": True,
                "primary_language": "Python",
                "stars": 189,
                "forks": 28,
                "knowledge_ids": ["microgrids", "edge-computing", "python", "kubernetes"],
                "translations": {
                    "en": {
                        "title": "Virtual Power Plant Simulator",
                        "description": "An emulator that stress-tests distributed energy resource coordination.",
                        "detailed_description": dedent(
                            """
                            Emulates household batteries, solar roofs, and demand response assets at scale.
                            Used by researchers to test control strategies before touching real infrastructure.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Simulador de Planta de Energia Virtual",
                        "description": "Emulador para validar la coordinacion de recursos distribuidos.",
                        "detailed_description": dedent(
                            """
                            Emula baterias residenciales, techos solares y respuesta a la demanda a gran escala.
                            Permite probar estrategias de control antes de aplicarlas en infraestructura real.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "slug": "energy-learning-platform",
                "project_type_slug": "product-experiences",
                "project_type_choice": "website",
                "order": 70,
                "featured": False,
                "primary_language": "TypeScript",
                "stars": 54,
                "forks": 6,
                "knowledge_ids": ["design-thinking", "react", "sustainability"],
                "demo_url": "https://demo.johndoe.energy/learning",
                "translations": {
                    "en": {
                        "title": "Energy Learning Platform",
                        "description": "A bite-sized learning experience for professionals entering clean energy.",
                        "detailed_description": dedent(
                            """
                            Crafted interactive modules, quizzes, and case studies that translate technical jargon
                            into business language. The platform supports mentoring programs and onboarding.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Plataforma de Aprendizaje en Energia",
                        "description": "Experiencia educativa para profesionales que ingresan a energia limpia.",
                        "detailed_description": dedent(
                            """
                            Desarrollamos modulos interactivos, cuestionarios y casos que traducen terminos tecnicos
                            al lenguaje de negocio. La plataforma respalda programas de mentoria y onboarding.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "slug": "climate-risk-reporting-tool",
                "project_type_slug": "consulting-engagement",
                "project_type_choice": "case_study",
                "order": 80,
                "featured": False,
                "primary_language": "Python",
                "stars": 63,
                "forks": 8,
                "knowledge_ids": ["data-analytics", "aws", "python", "design-thinking"],
                "translations": {
                    "en": {
                        "title": "Climate Risk Reporting Tool",
                        "description": "Rapid consultancy project that produced a climate disclosure dashboard.",
                        "detailed_description": dedent(
                            """
                            In six weeks we consolidated satellite data, adaptation plans, and financial KPIs
                            into an executive-ready scorecard used for regulatory reporting.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Herramienta de Reporte de Riesgo Climatico",
                        "description": "Proyecto de consultoria para entregar un tablero de divulgacion climatica.",
                        "detailed_description": dedent(
                            """
                            En seis semanas consolidamos datos satelitales, planes de adaptacion y KPIs financieros
                            en una tarjeta ejecutiva utilizada para reportes regulatorios.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "slug": "sustainability-scorecard-app",
                "project_type_slug": "product-experiences",
                "project_type_choice": "tool",
                "order": 90,
                "featured": True,
                "primary_language": "Python",
                "stars": 145,
                "forks": 22,
                "knowledge_ids": ["sustainability", "react", "django", "postgresql"],
                "featured_link_type": "post",
                "featured_post_slug": "sustainability-scorecards-that-stick",
                "translations": {
                    "en": {
                        "title": "Sustainability Scorecard App",
                        "description": "Mobile-first app that tracks sustainability commitments across teams.",
                        "detailed_description": dedent(
                            """
                            Provides shared metrics, narrative updates, and nudges so teams convert pledges
                            into visible progress. Includes offline support for field reporting.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Aplicacion de Indicadores de Sostenibilidad",
                        "description": "Aplicacion movil para seguir compromisos de sostenibilidad entre equipos.",
                        "detailed_description": dedent(
                            """
                            Ofrece metricas compartidas, actualizaciones narrativas y recordatorios para convertir
                            compromisos en progreso visible. Incluye soporte sin conexion para reportes en campo.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "slug": "microgrid-digital-twin",
                "project_type_slug": "research-initiative",
                "project_type_choice": "research",
                "order": 100,
                "featured": False,
                "primary_language": "Python",
                "stars": 88,
                "forks": 15,
                "knowledge_ids": ["microgrids", "edge-computing", "python", "kubernetes"],
                "translations": {
                    "en": {
                        "title": "Microgrid Digital Twin",
                        "description": "A digital twin that mirrors microgrid assets for scenario testing.",
                        "detailed_description": dedent(
                            """
                            Synchronises with real-world assets at one-minute intervals and allows engineers to
                            test how storms or demand spikes ripple through the network.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Gemelo Digital de Microred",
                        "description": "Gemelo digital que replica activos de microred para probar escenarios.",
                        "detailed_description": dedent(
                            """
                            Se sincroniza con activos reales cada minuto y deja evaluar como tormentas o picos
                            de demanda impactan la red.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "slug": "wind-farm-analytics-lab",
                "project_type_slug": "analytics-solutions",
                "project_type_choice": "process",
                "order": 110,
                "featured": False,
                "primary_language": "Python",
                "stars": 116,
                "forks": 17,
                "knowledge_ids": ["data-analytics", "machine-learning", "python", "power-bi"],
                "translations": {
                    "en": {
                        "title": "Wind Farm Analytics Lab",
                        "description": "Data platform that analyses turbine performance and wake interactions.",
                        "detailed_description": dedent(
                            """
                            Consolidated SCADA feeds, maintenance logs, and CFD simulations to highlight
                            underperforming turbines and recommend layout adjustments.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Laboratorio de Analitica para Parques Eolicos",
                        "description": "Plataforma de datos que analiza rendimiento de turbinas y efectos de estela.",
                        "detailed_description": dedent(
                            """
                            Consolidamos SCADA, bitacoras de mantenimiento y simulaciones CFD para destacar
                            turbinas con bajo rendimiento y proponer ajustes de layout.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "slug": "edge-iot-starter-kit",
                "project_type_slug": "energy-platforms",
                "project_type_choice": "template",
                "order": 120,
                "featured": False,
                "primary_language": "Python",
                "stars": 132,
                "forks": 19,
                "knowledge_ids": ["edge-computing", "kubernetes", "python", "docker"],
                "github_url": "https://github.com/johndoe-energy/edge-iot-kit",
                "translations": {
                    "en": {
                        "title": "Edge IoT Starter Kit",
                        "description": "Reference implementation for edge data collection in renewable plants.",
                        "detailed_description": dedent(
                            """
                            Provides containerised services, device management scripts, and telemetry schemas
                            that shorten the time from prototype to resilient field deployment.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Kit Inicial IoT en el Borde",
                        "description": "Implementacion de referencia para recopilar datos en plantas renovables.",
                        "detailed_description": dedent(
                            """
                            Incluye servicios en contenedores, scripts para gestionar dispositivos y esquemas de telemetria
                            que reducen el tiempo entre prototipo y despliegue en campo.
                            """
                        ).strip(),
                    },
                },
            },
        ]

        blog_post_lookup = blog_posts
        project_objects = []
        for data in projects_data:
            defaults = {
                "project_type_obj": project_types.get(data["project_type_slug"]),
                "project_type": data["project_type_choice"],
                "stars_count": data.get("stars", 0),
                "forks_count": data.get("forks", 0),
                "primary_language": data.get("primary_language", ""),
                "github_url": data.get("github_url", ""),
                "demo_url": data.get("demo_url", ""),
                "featured": data.get("featured", False),
                "order": data["order"],
                "visibility": "public",
                "featured_link_type": data.get("featured_link_type", "none"),
            }
            project, _ = Project.objects.update_or_create(
                slug=data["slug"],
                defaults=defaults,
            )
            self.assign_translations(project, data["translations"])

            knowledge_instances = [
                knowledge_bases[k]
                for k in data.get("knowledge_ids", [])
                if k in knowledge_bases
            ]
            project.knowledge_bases.set(knowledge_instances)

            if data.get("featured_link_type") == "post":
                project.featured_link_post = blog_post_lookup.get(
                    data.get("featured_post_slug")
                )
            else:
                project.featured_link_post = None
            project.save()
            project_objects.append(project)
        self.stdout.write(f"  Created/updated {len(project_objects)} projects")
        return project_objects
    def create_blog_posts(self, categories):
        now = timezone.now()
        posts_data = [
            {
                "slug": "modern-energy-dashboard-design",
                "category": "software-architecture",
                "days_ago": 7,
                "reading_time": 8,
                "featured": True,
                "tags": "energy, dashboards, ux",
                "translations": {
                    "en": {
                        "title": "Modern Energy Dashboard Design",
                        "excerpt": "Principles for crafting dashboards that operators actually trust.",
                        "content": dedent(
                            """
                            # Modern Energy Dashboard Design

                            The best dashboards feel calm even when the grid is not. We explore layout patterns,
                            typography choices, and how to translate alarms into context the team can understand.

                            ## Key Sections
                            - Visual hierarchy for complex telemetry
                            - Summaries versus detailed drilldowns
                            - Designing for the dark site during outages
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Diseno Moderno de Dashboards de Energia",
                        "excerpt": "Principios para crear tableros que los operadores confian.",
                        "content": dedent(
                            """
                            # Diseno Moderno de Dashboards de Energia

                            Los mejores tableros transmiten calma aun cuando la red esta bajo estres.
                            Revisamos patrones de layout, tipografia y como traducir alarmas en contexto util.

                            ## Secciones Clave
                            - Jerarquia visual para telemetria compleja
                            - Resumenes frente a vistas detalladas
                            - Diseno para el modo oscuro cuando hay fallas
                            """
                        ).strip(),
                    },
                },
            },
            {
                "slug": "microgrid-fundamentals-for-digital-teams",
                "category": "renewable-energy",
                "days_ago": 14,
                "reading_time": 9,
                "featured": False,
                "tags": "microgrids, strategy",
                "translations": {
                    "en": {
                        "title": "Microgrid Fundamentals for Digital Teams",
                        "excerpt": "A primer for software engineers joining microgrid projects.",
                        "content": dedent(
                            """
                            # Microgrid Fundamentals for Digital Teams

                            Software engineers bring enormous value to distributed energy projects,
                            but the domain language can be overwhelming. We unpack dispatch strategies,
                            control layers, and the telemetry that matters most in the field.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Fundamentos de Microredes para Equipos Digitales",
                        "excerpt": "Guia rapida para ingenieros de software que se unen a proyectos de microredes.",
                        "content": dedent(
                            """
                            # Fundamentos de Microredes para Equipos Digitales

                            Los ingenieros de software aportan gran valor en energia distribuida,
                            pero el vocabulario puede intimidar. Desglosamos estrategias de despacho,
                            capas de control y telemetria clave en campo.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "slug": "battery-analytics-notebook-tutorial",
                "category": "tutorials",
                "days_ago": 21,
                "reading_time": 10,
                "featured": False,
                "tags": "batteries, notebook, tutorial",
                "translations": {
                    "en": {
                        "title": "Battery Analytics Notebook Tutorial",
                        "excerpt": "Walk-through of a notebook that diagnoses battery health with open data.",
                        "content": dedent(
                            """
                            # Battery Analytics Notebook Tutorial

                            In this hands-on session we ingest public datasets, engineer features,
                            and train a gradient boosting model that predicts capacity fade.
                            The notebook is ready to run in Jupyter or VS Code.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Tutorial de Notebook para Analitica de Baterias",
                        "excerpt": "Paso a paso para diagnosticar salud de baterias con datos abiertos.",
                        "content": dedent(
                            """
                            # Tutorial de Notebook para Analitica de Baterias

                            Ingerimos datos publicos, creamos features y entrenamos un modelo
                            de gradient boosting que estima la perdida de capacidad.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "slug": "sustainability-scorecards-that-stick",
                "category": "sustainability",
                "days_ago": 28,
                "reading_time": 7,
                "featured": True,
                "tags": "sustainability, leadership",
                "translations": {
                    "en": {
                        "title": "Sustainability Scorecards That Stick",
                        "excerpt": "How to build sustainability scorecards that survive the quarter.",
                        "content": dedent(
                            """
                            # Sustainability Scorecards That Stick

                            We review common pitfalls, share templates, and outline rituals that keep
                            metrics human and actionable for teams across the organisation.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Scorecards de Sostenibilidad que Funcionan",
                        "excerpt": "Como crear scorecards de sostenibilidad que duran mas de un trimestre.",
                        "content": dedent(
                            """
                            # Scorecards de Sostenibilidad que Funcionan

                            Revisamos errores frecuentes, compartimos plantillas y rituales que
                            convierten los indicadores en acciones concretas.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "slug": "ai-for-grid-operations",
                "category": "data-science",
                "days_ago": 35,
                "reading_time": 11,
                "featured": False,
                "tags": "ai, grid, operations",
                "translations": {
                    "en": {
                        "title": "AI for Grid Operations",
                        "excerpt": "Where AI already helps operators and where it still struggles.",
                        "content": dedent(
                            """
                            # AI for Grid Operations

                            From anomaly detection to outage prediction we explore successful deployments,
                            governance guardrails, and practical steps to bring data science closer to the control room.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "IA para Operaciones de Red",
                        "excerpt": "Donde la IA ayuda hoy y donde aun tropieza.",
                        "content": dedent(
                            """
                            # IA para Operaciones de Red

                            Analizamos casos de deteccion de anomalias, prediccion de fallas y
                            reglas de gobernanza para acercar la ciencia de datos a la sala de control.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "slug": "review-of-open-bess-platforms",
                "category": "product-reviews",
                "days_ago": 42,
                "reading_time": 6,
                "featured": False,
                "tags": "bess, review",
                "translations": {
                    "en": {
                        "title": "Review of Open BESS Platforms",
                        "excerpt": "Comparing three open-source battery management platforms.",
                        "content": dedent(
                            """
                            # Review of Open BESS Platforms

                            We evaluate community support, security posture, and extensibility
                            for developers that need a head start on industrial battery projects.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Resena de Plataformas BESS Abiertas",
                        "excerpt": "Comparativa de tres plataformas open source para gestionar baterias.",
                        "content": dedent(
                            """
                            # Resena de Plataformas BESS Abiertas

                            Evaluamos soporte comunitario, postura de seguridad y extensibilidad
                            para equipos que inician proyectos de almacenamiento.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "slug": "climate-risk-modeling-playbook",
                "category": "data-science",
                "days_ago": 49,
                "reading_time": 9,
                "featured": False,
                "tags": "climate, risk, modeling",
                "translations": {
                    "en": {
                        "title": "Climate Risk Modelling Playbook",
                        "excerpt": "A checklist for building transparent climate risk models.",
                        "content": dedent(
                            """
                            # Climate Risk Modelling Playbook

                            Climate risk is not just about data. We cover stakeholder mapping,
                            model explainability, and how to communicate uncertainty responsibly.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Playbook de Modelado de Riesgo Climatico",
                        "excerpt": "Lista de verificacion para modelos de riesgo climaticos transparentes.",
                        "content": dedent(
                            """
                            # Playbook de Modelado de Riesgo Climatico

                            El riesgo climatico no se trata solo de datos. Hablamos de actores,
                            explicabilidad y comunicaciones responsables sobre incertidumbre.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "slug": "field-notes-from-island-microgrids",
                "category": "career-notes",
                "days_ago": 56,
                "reading_time": 8,
                "featured": False,
                "tags": "microgrids, field",
                "translations": {
                    "en": {
                        "title": "Field Notes from Island Microgrids",
                        "excerpt": "Practical lessons gathered while commissioning microgrids on islands.",
                        "content": dedent(
                            """
                            # Field Notes from Island Microgrids

                            Stories about logistics, community partnerships, and writing software
                            while balancing on shipping containers.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Notas de Campo en Microredes Insulares",
                        "excerpt": "Lecciones practicas al comisionar microredes en islas.",
                        "content": dedent(
                            """
                            # Notas de Campo en Microredes Insulares

                            Historias sobre logistica, alianzas comunitarias y escribir software
                            mientras te equilibras sobre contenedores.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "slug": "team-handbook-for-energy-startups",
                "category": "software-architecture",
                "days_ago": 63,
                "reading_time": 7,
                "featured": False,
                "tags": "startup, handbook",
                "translations": {
                    "en": {
                        "title": "Team Handbook for Energy Startups",
                        "excerpt": "A lightweight handbook template for early energy teams.",
                        "content": dedent(
                            """
                            # Team Handbook for Energy Startups

                            Policies, rituals, and checklists that keep distributed teams aligned
                            as they scale product and grid partnerships.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Manual de Equipo para Startups de Energia",
                        "excerpt": "Plantilla ligera de manual para equipos de energia en etapas tempranas.",
                        "content": dedent(
                            """
                            # Manual de Equipo para Startups de Energia

                            Politicas, rituales y listas de verificacion para mantener equipos distribuidos alineados
                            mientras escalan producto y alianzas con la red.
                            """
                        ).strip(),
                    },
                },
            },
            {
                "slug": "edge-computing-in-solar-farms",
                "category": "renewable-energy",
                "days_ago": 70,
                "reading_time": 8,
                "featured": False,
                "tags": "edge, solar",
                "translations": {
                    "en": {
                        "title": "Edge Computing in Solar Farms",
                        "excerpt": "Why edge computing matters for solar plant operators.",
                        "content": dedent(
                            """
                            # Edge Computing in Solar Farms

                            We explore latency budgets, maintenance realities, and how to orchestrate
                            workloads that straddle the edge and the cloud.
                            """
                        ).strip(),
                    },
                    "es": {
                        "title": "Edge Computing en Plantas Solares",
                        "excerpt": "Por que el edge computing importa para operadores solares.",
                        "content": dedent(
                            """
                            # Edge Computing en Plantas Solares

                            Analizamos latencia, mantenimiento y como orquestar cargas entre el borde y la nube.
                            """
                        ).strip(),
                    },
                },
            },
        ]

        posts = {}
        for data in posts_data:
            publish_date = now - timedelta(days=data["days_ago"])
            defaults = {
                "publish_date": publish_date,
                "reading_time": data["reading_time"],
                "featured": data["featured"],
                "tags": data.get("tags", ""),
                "status": "published",
                "category": categories.get(data["category"]),
            }
            post, _ = BlogPost.objects.update_or_create(
                slug=data["slug"],
                defaults=defaults,
            )
            self.assign_translations(post, data["translations"])
            posts[data["slug"]] = post
        self.stdout.write(f"  Created/updated {len(posts)} blog posts")
        return posts

    def create_contacts(self):
        contacts_data = [
            {
                "name": "Elena Morales",
                "email": "elena.morales@example.com",
                "subject": "Partnership on community microgrids",
                "message": "We are developing a microgrid program for coastal villages and would love to learn from your approach.",
                "read": False,
            },
            {
                "name": "Marcus Lee",
                "email": "marcus.lee@example.com",
                "subject": "Keynote invitation",
                "message": "Your work on sustainability scorecards caught our eye. Would you speak at our energy innovation summit?",
                "read": False,
            },
            {
                "name": "Aisha Grant",
                "email": "aisha.grant@example.com",
                "subject": "Code review request",
                "message": "We forked the edge IoT starter kit and want a professional review before deploying to site.",
                "read": True,
            },
        ]

        contacts = []
        for data in contacts_data:
            contact, _ = Contact.objects.update_or_create(
                email=data["email"],
                subject=data["subject"],
                defaults=data,
            )
            contacts.append(contact)
        self.stdout.write(f"  Created/updated {len(contacts)} sample contacts")
        return contacts
