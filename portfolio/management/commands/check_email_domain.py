from django.core.management.base import BaseCommand
from portfolio.email_service import EmailDomainChecker


class Command(BaseCommand):
    help = 'Verifica la compatibilidad de un dominio de email con Gmail'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email a verificar')

    def handle(self, *args, **options):
        email = options['email']
        
        self.stdout.write(self.style.SUCCESS(f'🔍 Verificando compatibilidad: {email}'))
        self.stdout.write('')
        
        result = EmailDomainChecker.check_domain_compatibility(email)
        
        if result['compatible']:
            if result['level'] == 'high':
                color = self.style.SUCCESS
                icon = '✅'
            elif result['level'] == 'medium':
                color = self.style.WARNING
                icon = '⚠️'
            else:
                color = self.style.ERROR
                icon = '🐌'
            
            self.stdout.write(color(f'{icon} Compatibilidad: {result["level"].upper()}'))
            self.stdout.write(f'⏰ Tiempo estimado de entrega: {result["delivery_time"]}')
            self.stdout.write(f'💡 Recomendación: {result["recommendation"]}')
        else:
            reason = result.get('reason', 'Dominio no compatible')
            self.stdout.write(self.style.ERROR(f'❌ No compatible: {reason}'))
        
        self.stdout.write('')
        
        if result.get('level') == 'low':
            self.stdout.write(self.style.WARNING('⚠️  Dominio externo detectado:'))
            self.stdout.write('   • Los emails pueden tardar hasta 30 minutos')
            self.stdout.write('   • Pueden ser bloqueados por filtros anti-spam')
            self.stdout.write('   • Revisa la carpeta de spam del destinatario')
            self.stdout.write('   • Considera usar un servicio de email profesional')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🔍 Verificación completada!'))