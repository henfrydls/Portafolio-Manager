"""
Comando de Django para mostrar estadísticas de visitas del sitio.

Este comando muestra un resumen de las visitas registradas, separando
las visitas públicas de las de administración.

Uso:
    python manage.py visit_stats
"""

from django.core.management.base import BaseCommand
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from portfolio.models import PageVisit


class Command(BaseCommand):
    help = 'Muestra estadísticas de visitas del sitio'

    def handle(self, *args, **options):
        # Rutas de administración
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

        # Obtener estadísticas
        total_visits = PageVisit.objects.count()
        admin_visits = PageVisit.objects.filter(admin_conditions).count()
        public_visits = total_visits - admin_visits

        # Estadísticas por período
        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        today_visits = PageVisit.objects.filter(
            timestamp__date=today
        ).exclude(admin_conditions).count()

        week_visits = PageVisit.objects.filter(
            timestamp__gte=week_ago
        ).exclude(admin_conditions).count()

        month_visits = PageVisit.objects.filter(
            timestamp__gte=month_ago
        ).exclude(admin_conditions).count()

        # Páginas más visitadas (solo públicas)
        popular_pages = PageVisit.objects.exclude(admin_conditions).values(
            'page_url', 'page_title'
        ).annotate(
            visits=Count('id')
        ).order_by('-visits')[:10]

        # Mostrar estadísticas
        self.stdout.write(self.style.SUCCESS('=== ESTADÍSTICAS DE VISITAS ==='))
        self.stdout.write('')
        
        self.stdout.write(f'📊 Total de visitas registradas: {total_visits}')
        self.stdout.write(f'🌐 Visitas del sitio público: {public_visits}')
        self.stdout.write(f'⚙️  Visitas de administración: {admin_visits}')
        self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS('=== VISITAS PÚBLICAS POR PERÍODO ==='))
        self.stdout.write(f'📅 Hoy: {today_visits} visitas')
        self.stdout.write(f'📅 Última semana: {week_visits} visitas')
        self.stdout.write(f'📅 Último mes: {month_visits} visitas')
        self.stdout.write('')
        
        if popular_pages:
            self.stdout.write(self.style.SUCCESS('=== PÁGINAS MÁS VISITADAS (PÚBLICAS) ==='))
            for i, page in enumerate(popular_pages, 1):
                title = page['page_title'] or 'Sin título'
                url = page['page_url']
                visits = page['visits']
                self.stdout.write(f'{i:2d}. {title} ({url}) - {visits} visitas')
        else:
            self.stdout.write(self.style.WARNING('No hay visitas públicas registradas.'))
        
        self.stdout.write('')
        
        if admin_visits > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  Hay {admin_visits} visitas de administración que pueden limpiarse '
                    'con: python manage.py cleanup_admin_visits'
                )
            )