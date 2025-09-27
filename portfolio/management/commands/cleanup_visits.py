from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from portfolio.middleware import PageVisitMiddleware
from portfolio.models import PageVisit


class Command(BaseCommand):
    help = 'Limpia visitas inválidas del sistema de tracking'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué se eliminaría sin hacer cambios reales',
        )
        parser.add_argument(
            '--older-than',
            type=int,
            help='Eliminar visitas más antiguas que X días',
        )
        parser.add_argument(
            '--show-examples',
            action='store_true',
            help='Muestra ejemplos de visitas que serán eliminadas',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🧹 Iniciando limpieza de visitas inválidas...')
        )

        # Mostrar estadísticas iniciales
        total_visits = PageVisit.objects.count()
        self.stdout.write(f'📊 Total de visitas registradas: {total_visits}')

        if options['show_examples']:
            self._show_invalid_examples()

        # Limpieza por antigüedad si se especifica
        if options['older_than']:
            self._cleanup_old_visits(options['older_than'], options['dry_run'])

        # Limpieza de visitas inválidas
        deleted_count = self._cleanup_invalid_visits(options['dry_run'])

        # Mostrar estadísticas finales
        if not options['dry_run']:
            final_visits = PageVisit.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Limpieza completada!\n'
                    f'   Visitas eliminadas: {deleted_count}\n'
                    f'   Visitas restantes: {final_visits}'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'🔍 Modo dry-run: Se eliminarían {deleted_count} visitas'
                )
            )

    def _show_invalid_examples(self):
        """Muestra ejemplos de visitas inválidas que serán eliminadas"""
        self.stdout.write('\n🔍 Ejemplos de visitas inválidas encontradas:')
        
        # Visitas con .well-known
        well_known_visits = PageVisit.objects.filter(
            page_url__icontains='.well-known'
        )[:3]
        
        if well_known_visits:
            self.stdout.write('   📱 Solicitudes automáticas de navegadores:')
            for visit in well_known_visits:
                self.stdout.write(f'     - {visit.page_url}')

        # Visitas de bots
        bot_visits = PageVisit.objects.filter(
            user_agent__icontains='bot'
        )[:3]
        
        if bot_visits:
            self.stdout.write('   🤖 Visitas de bots:')
            for visit in bot_visits:
                self.stdout.write(f'     - {visit.page_url} | {visit.user_agent[:50]}...')

        # Visitas a rutas de admin
        admin_visits = PageVisit.objects.filter(
            page_url__startswith='/admin/'
        )[:3]
        
        if admin_visits:
            self.stdout.write('   ⚙️ Visitas a páginas de administración:')
            for visit in admin_visits:
                self.stdout.write(f'     - {visit.page_url}')

    def _cleanup_old_visits(self, days, dry_run):
        """Elimina visitas más antiguas que el número de días especificado"""
        cutoff_date = timezone.now() - timedelta(days=days)
        old_visits = PageVisit.objects.filter(timestamp__lt=cutoff_date)
        count = old_visits.count()
        
        if count > 0:
            self.stdout.write(f'📅 Visitas más antiguas que {days} días: {count}')
            if not dry_run:
                old_visits.delete()
                self.stdout.write(
                    self.style.SUCCESS(f'   ✅ {count} visitas antiguas eliminadas')
                )
        else:
            self.stdout.write(f'📅 No hay visitas más antiguas que {days} días')

    def _cleanup_invalid_visits(self, dry_run):
        """Elimina visitas inválidas usando el middleware"""
        if dry_run:
            # Para dry-run, contar sin eliminar
            from django.db.models import Q
            
            invalid_conditions = Q()
            
            # Agregar condiciones para rutas excluidas
            for excluded_path in PageVisitMiddleware.EXCLUDED_PATHS:
                invalid_conditions |= Q(page_url__startswith=excluded_path)
            
            # Agregar condiciones para patrones excluidos
            for pattern in PageVisitMiddleware.EXCLUDED_PATTERNS:
                invalid_conditions |= Q(page_url__icontains=pattern)
            
            # Agregar condiciones para user agents de bots
            for bot in PageVisitMiddleware.BOT_USER_AGENTS:
                invalid_conditions |= Q(user_agent__icontains=bot)
            
            # Agregar condiciones para herramientas de desarrollo
            for dev_pattern in PageVisitMiddleware.DEV_TOOL_PATTERNS:
                invalid_conditions |= Q(user_agent__icontains=dev_pattern)
            
            return PageVisit.objects.filter(invalid_conditions).count()
        else:
            return PageVisitMiddleware.cleanup_invalid_visits()