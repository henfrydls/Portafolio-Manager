import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Verifica si las variables del archivo .env se están cargando correctamente'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Verificando carga del archivo .env...'))
        self.stdout.write('')
        
        # Variables importantes del .env
        env_vars = {
            'PROJECT_NAME': 'Nombre del proyecto',
            'SECRET_KEY': 'Clave secreta de Django',
            'DEBUG': 'Modo debug',
            'DOMAIN': 'Dominio principal',
            'EMAIL_HOST': 'Servidor de email',
            'EMAIL_HOST_USER': 'Usuario de email',
            'EMAIL_HOST_PASSWORD': 'Contraseña de email',
            'DEFAULT_FROM_EMAIL': 'Email por defecto',
            'ALLOWED_HOSTS_DEV': 'Hosts permitidos en desarrollo',
        }
        
        self.stdout.write(self.style.WARNING('📋 Variables del archivo .env:'))
        self.stdout.write('')
        
        loaded_count = 0
        total_count = len(env_vars)
        
        for var_name, description in env_vars.items():
            value = os.environ.get(var_name)
            if value:
                # Ocultar valores sensibles
                if 'PASSWORD' in var_name or 'SECRET' in var_name:
                    display_value = '*' * len(value) if len(value) > 0 else 'No definido'
                else:
                    display_value = value
                
                self.stdout.write(f'  ✅ {var_name}: {display_value}')
                loaded_count += 1
            else:
                self.stdout.write(f'  ❌ {var_name}: No definido')
        
        self.stdout.write('')
        
        # Mostrar estadísticas
        if loaded_count == total_count:
            self.stdout.write(self.style.SUCCESS(f'🎉 Todas las variables están cargadas ({loaded_count}/{total_count})'))
        elif loaded_count > 0:
            self.stdout.write(self.style.WARNING(f'⚠️  Algunas variables están cargadas ({loaded_count}/{total_count})'))
        else:
            self.stdout.write(self.style.ERROR('❌ Ninguna variable del .env está cargada'))
        
        self.stdout.write('')
        
        # Verificar configuración de Django
        self.stdout.write(self.style.WARNING('⚙️  Configuración de Django:'))
        self.stdout.write(f'  • DEBUG: {settings.DEBUG}')
        self.stdout.write(f'  • ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
        self.stdout.write(f'  • EMAIL_HOST: {getattr(settings, "EMAIL_HOST", "No configurado")}')
        self.stdout.write(f'  • DEFAULT_FROM_EMAIL: {getattr(settings, "DEFAULT_FROM_EMAIL", "No configurado")}')
        
        self.stdout.write('')
        
        # Verificar si el archivo .env existe
        env_file_path = os.path.join(settings.BASE_DIR, '.env')
        if os.path.exists(env_file_path):
            self.stdout.write(self.style.SUCCESS('✅ Archivo .env encontrado'))
        else:
            self.stdout.write(self.style.ERROR('❌ Archivo .env NO encontrado'))
            self.stdout.write('   Crea el archivo .env en la raíz del proyecto')
        
        # Verificar si python-dotenv está instalado
        try:
            import dotenv
            self.stdout.write(self.style.SUCCESS('✅ python-dotenv está instalado'))
        except ImportError:
            self.stdout.write(self.style.ERROR('❌ python-dotenv NO está instalado'))
            self.stdout.write('   Instala con: pip install python-dotenv')
        
        self.stdout.write('')
        
        # Consejos
        self.stdout.write(self.style.WARNING('💡 Consejos:'))
        if loaded_count < total_count:
            self.stdout.write('   • Verifica que el archivo .env esté en la raíz del proyecto')
            self.stdout.write('   • Asegúrate de que python-dotenv esté instalado')
            self.stdout.write('   • Reinicia el servidor después de cambiar el .env')
        
        self.stdout.write('   • No subas el archivo .env al repositorio')
        self.stdout.write('   • Usa .env.example como plantilla')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🔍 Verificación completada!'))