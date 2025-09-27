"""
Comando de Django para limpiar visitas de páginas de administración.

Este comando elimina todas las visitas registradas que corresponden a páginas
de administración, dejando solo las visitas del sitio público para métricas limpias.

Uso:
    python manage.py cleanup_admin_visits
    python manage.py cleanup_admin_visits --dry-run  # Solo mostrar qué se eliminaría
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from portfolio.models import PageVisit


class Command(BaseCommand):
    help = 'Limpia visitas de páginas de administración de las métricas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué visitas se eliminarían sin eliminarlas realmente',
        )

    def handle(self, *args, **options):
        # Rutas de administración a excluir
        admin_paths = [
            '/admin/',
            '/dashboard/',
            '/analytics/',
            '/admin-dashboard/',
            '/admin-analytics/',
            '/login/',
            '/logout/',
            '/password-change/',
            '/manage/',
            '/api/',
        ]

        # Construir query para visitas de administración
        admin_conditions = Q()
        for admin_path in admin_paths:
            admin_conditions |= Q(page_url__startswith=admin_path)

        # Obtener visitas de administración
        admin_visits = PageVisit.objects.filter(admin_conditions)
        count = admin_visits.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('No se encontraron visitas de administración para limpiar.')
            )
            return

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Se eliminarían {count} visitas de administración:')
            )
            
            # Mostrar ejemplos de las visitas que se eliminarían
            sample_visits = admin_visits[:10]
            for visit in sample_visits:
                self.stdout.write(f'  - {visit.page_url} ({visit.timestamp})')
            
            if count > 10:
                self.stdout.write(f'  ... y {count - 10} más')
                
        else:
            # Confirmar antes de eliminar
            confirm = input(f'¿Estás seguro de que quieres eliminar {count} visitas de administración? (y/N): ')
            
            if confirm.lower() in ['y', 'yes', 'sí', 'si']:
                deleted_count, _ = admin_visits.delete()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Eliminadas {deleted_count} visitas de administración.')
                )
                
                # Mostrar estadísticas después de la limpieza
                remaining_visits = PageVisit.objects.count()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Quedan {remaining_visits} visitas del sitio público.')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Operación cancelada.')
                )