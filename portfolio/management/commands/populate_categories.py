"""
Comando para poblar las categorías iniciales del blog.
"""
from django.core.management.base import BaseCommand
from portfolio.models import Category


class Command(BaseCommand):
    help = 'Pobla las categorías iniciales del blog'

    def handle(self, *args, **options):
        categories_data = [
            {
                'name': 'Noticia',
                'slug': 'noticia',
                'description': 'Actualizaciones profesionales y noticias del sector',
                'order': 1
            },
            {
                'name': 'Tutorial',
                'slug': 'tutorial',
                'description': 'Guías técnicas y tutoriales paso a paso',
                'order': 2
            },
            {
                'name': 'Opinión',
                'slug': 'opinion',
                'description': 'Reflexiones personales y análisis del sector',
                'order': 3
            },
            {
                'name': 'Proyecto',
                'slug': 'proyecto',
                'description': 'Detalles y documentación de proyectos',
                'order': 4
            },
            {
                'name': 'Carrera',
                'slug': 'carrera',
                'description': 'Experiencias profesionales y desarrollo de carrera',
                'order': 5
            },
            {
                'name': 'Tecnología',
                'slug': 'tecnologia',
                'description': 'Artículos sobre nuevas tecnologías y herramientas',
                'order': 6
            }
        ]

        created_count = 0
        updated_count = 0

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'[+] Categoria creada: {category.name}')
                )
            else:
                # Actualizar campos existentes
                for field, value in cat_data.items():
                    if field != 'slug':  # No actualizar el slug
                        setattr(category, field, value)
                category.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'[*] Categoria actualizada: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n[RESUMEN] Resumen:'
                f'\n   - {created_count} categorías creadas'
                f'\n   - {updated_count} categorías actualizadas'
                f'\n   - {len(categories_data)} categorías totales disponibles'
            )
        )

        # Mostrar tabla de categorías
        self.stdout.write('\n[CATEGORIAS] Categorías disponibles:')
        self.stdout.write('-' * 60)
        for cat in Category.objects.all().order_by('order'):
            self.stdout.write(
                f'{cat.order}. {cat.name:<15} | {cat.slug}'
            )