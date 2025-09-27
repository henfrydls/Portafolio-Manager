"""
Comando para poblar los tipos de proyectos iniciales.
"""
from django.core.management.base import BaseCommand
from portfolio.models import ProjectType


class Command(BaseCommand):
    help = 'Pobla los tipos de proyectos iniciales'

    def handle(self, *args, **options):
        project_types_data = [
            {
                'name': 'Framework',
                'slug': 'framework',
                'description': 'Sistema base reutilizable que proporciona funcionalidad común para desarrollo de aplicaciones',
                'order': 1
            },
            {
                'name': 'Tool',
                'slug': 'tool',
                'description': 'Herramienta específica diseñada para resolver problemas técnicos o automatizar procesos',
                'order': 2
            },
            {
                'name': 'Website',
                'slug': 'website',
                'description': 'Sitio web o aplicación web completa con funcionalidades interactivas',
                'order': 3
            },
            {
                'name': 'Mobile App',
                'slug': 'mobile-app',
                'description': 'Aplicación móvil nativa o híbrida para dispositivos Android e iOS',
                'order': 4
            },
            {
                'name': 'Desktop App',
                'slug': 'desktop-app',
                'description': 'Aplicación de escritorio para sistemas operativos Windows, macOS o Linux',
                'order': 5
            },
            {
                'name': 'Library',
                'slug': 'library',
                'description': 'Biblioteca de código reutilizable que otros desarrolladores pueden integrar',
                'order': 6
            },
            {
                'name': 'API',
                'slug': 'api',
                'description': 'Interfaz de programación que permite comunicación entre diferentes aplicaciones',
                'order': 7
            },
            {
                'name': 'Template',
                'slug': 'template',
                'description': 'Plantilla o tema prediseñado para sitios web, aplicaciones o documentos',
                'order': 8
            },
            {
                'name': 'Dataset',
                'slug': 'dataset',
                'description': 'Conjunto de datos estructurados para análisis, investigación o machine learning',
                'order': 9
            },
            {
                'name': 'Consulting',
                'slug': 'consulting',
                'description': 'Proyecto de consultoría tecnológica o estratégica para organizaciones',
                'order': 10
            },
            {
                'name': 'Strategy',
                'slug': 'strategy',
                'description': 'Desarrollo de estrategias digitales, transformación tecnológica y planificación',
                'order': 11
            },
            {
                'name': 'Research',
                'slug': 'research',
                'description': 'Investigación tecnológica, análisis de mercado o estudios especializados',
                'order': 12
            },
            {
                'name': 'Process',
                'slug': 'process',
                'description': 'Mejora y optimización de procesos empresariales o técnicos',
                'order': 13
            },
            {
                'name': 'Training',
                'slug': 'training',
                'description': 'Programas de capacitación, cursos o materiales educativos tecnológicos',
                'order': 14
            },
            {
                'name': 'Case Study',
                'slug': 'case-study',
                'description': 'Documentación detallada de proyectos exitosos y lecciones aprendidas',
                'order': 15
            },
            {
                'name': 'Implementation',
                'slug': 'implementation',
                'description': 'Implementación de soluciones tecnológicas en entornos empresariales',
                'order': 16
            }
        ]

        created_count = 0
        updated_count = 0

        for type_data in project_types_data:
            project_type, created = ProjectType.objects.get_or_create(
                slug=type_data['slug'],
                defaults=type_data
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'[+] Tipo de proyecto creado: {project_type.name}')
                )
            else:
                # Actualizar campos existentes
                for field, value in type_data.items():
                    if field != 'slug':  # No actualizar el slug
                        setattr(project_type, field, value)
                project_type.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'[*] Tipo de proyecto actualizado: {project_type.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n[RESUMEN] Resumen:'
                f'\n   - {created_count} tipos de proyectos creados'
                f'\n   - {updated_count} tipos de proyectos actualizados'
                f'\n   - {len(project_types_data)} tipos de proyectos totales disponibles'
            )
        )

        # Mostrar tabla de tipos de proyectos
        self.stdout.write('\n[TIPOS] Tipos de proyectos disponibles:')
        self.stdout.write('-' * 80)
        for ptype in ProjectType.objects.all().order_by('order'):
            self.stdout.write(
                f'{ptype.order:2d}. {ptype.name:<20} | {ptype.slug}'
            )