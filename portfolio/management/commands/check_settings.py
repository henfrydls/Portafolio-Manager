import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Verifica qué archivo de configuración se está usando'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('⚙️  Verificando configuración de Django...'))
        self.stdout.write('')
        
        # Mostrar DJANGO_SETTINGS_MODULE
        settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
        self.stdout.write(self.style.WARNING('📋 Configuración actual:'))
        self.stdout.write(f'  • DJANGO_SETTINGS_MODULE: {settings_module}')
        
        # Determinar el entorno basado en el módulo de configuración
        if 'development' in settings_module:
            env_type = 'DEVELOPMENT'
            color = self.style.SUCCESS
        elif 'production' in settings_module:
            env_type = 'PRODUCTION'
            color = self.style.ERROR
        elif 'staging' in settings_module:
            env_type = 'STAGING'
            color = self.style.WARNING
        else:
            env_type = 'UNKNOWN'
            color = self.style.ERROR
        
        self.stdout.write(f'  • Entorno detectado: {color(env_type)}')
        self.stdout.write('')
        
        # Mostrar configuraciones importantes
        self.stdout.write(self.style.WARNING('🔧 Configuraciones importantes:'))
        self.stdout.write(f'  • DEBUG: {settings.DEBUG}')
        self.stdout.write(f'  • ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
        
        # Mostrar base de datos
        db_config = settings.DATABASES['default']
        db_name = db_config.get('NAME', 'No configurado')
        if isinstance(db_name, str) and db_name.endswith('.sqlite3'):
            db_display = os.path.basename(db_name)
        else:
            db_display = str(db_name)
        
        self.stdout.write(f'  • Base de datos: {db_display}')
        self.stdout.write(f'  • EMAIL_HOST: {getattr(settings, "EMAIL_HOST", "No configurado")}')
        
        # Verificar si hay variable ENVIRONMENT en settings
        environment_var = getattr(settings, 'ENVIRONMENT', 'No definido')
        self.stdout.write(f'  • Variable ENVIRONMENT: {environment_var}')
        
        self.stdout.write('')
        
        # Mostrar archivo de configuración real
        settings_file = settings.SETTINGS_MODULE
        self.stdout.write(self.style.WARNING('📁 Archivo de configuración:'))
        self.stdout.write(f'  • {settings_file}')
        
        # Verificar .env
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('📄 Variables del .env:'))
        env_django_settings = os.environ.get('DJANGO_SETTINGS_MODULE')
        self.stdout.write(f'  • DJANGO_SETTINGS_MODULE en .env: {env_django_settings}')
        
        # Consejos
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('💡 Para cambiar el entorno:'))
        self.stdout.write('  1. Modifica DJANGO_SETTINGS_MODULE en el archivo .env')
        self.stdout.write('  2. Reinicia el servidor completamente')
        self.stdout.write('  3. Verifica con: python manage.py check_settings')
        
        self.stdout.write('')
        if env_type == 'PRODUCTION':
            self.stdout.write(self.style.ERROR('⚠️  CUIDADO: Estás en modo PRODUCCIÓN'))
            self.stdout.write('   • DEBUG debería ser False')
            self.stdout.write('   • Verifica ALLOWED_HOSTS')
            self.stdout.write('   • Usa base de datos externa (no SQLite)')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Verificación completada!'))