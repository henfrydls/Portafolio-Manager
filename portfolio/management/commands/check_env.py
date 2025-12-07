import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Verifica si las variables del archivo .env se están cargando correctamente'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Verificando carga del archivo .env...'))
        self.stdout.write('')

        # Detectar el entorno actual
        settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.development')
        environment = self._detect_environment(settings_module)

        self.stdout.write(f'🌍 Entorno detectado: {environment.upper()}')
        self.stdout.write('')

        # Leer valores de ejemplo del .env.example
        example_values = self._load_example_values()

        # Variables comunes a todos los entornos
        common_vars = {
            'PROJECT_NAME': 'Nombre del proyecto',
            'SECRET_KEY': 'Clave secreta de Django',
            'DEBUG': 'Modo debug',
            'EMAIL_HOST': 'Servidor de email',
            'EMAIL_HOST_USER': 'Usuario de email',
            'EMAIL_HOST_PASSWORD': 'Contraseña de email',
        }

        # Variables específicas por entorno
        env_specific_vars = self._get_environment_vars(environment)

        # Combinar variables comunes y específicas del entorno
        env_vars = {**common_vars, **env_specific_vars}

        self.stdout.write(self.style.WARNING('📋 Variables del archivo .env:'))
        self.stdout.write('')

        loaded_count = 0
        total_count = len(env_vars)

        for var_name, description in env_vars.items():
            value = os.environ.get(var_name)
            if value:
                # Verificar si el valor es igual al del ejemplo (placeholder)
                example_value = example_values.get(var_name, '')
                is_placeholder = self._is_placeholder_value(var_name, value, example_value)

                # Verificar advertencias de seguridad específicas
                security_warning = self._check_security_warning(var_name, value)

                # Ocultar valores sensibles
                if 'PASSWORD' in var_name or 'SECRET' in var_name:
                    display_value = '*' * len(value) if len(value) > 0 else 'No definido'
                else:
                    display_value = value

                if security_warning:
                    self.stdout.write(f'  ⚠️  {var_name}: {display_value} {security_warning}')
                    # Variables con advertencias de seguridad no cuentan como válidas
                elif is_placeholder:
                    self.stdout.write(f'  ⚠️  {var_name}: {display_value} (valor de ejemplo, actualizar)')
                else:
                    self.stdout.write(f'  ✅ {var_name}: {display_value}')
                    loaded_count += 1
            else:
                self.stdout.write(f'  ❌ {var_name}: No definido')

        self.stdout.write('')

        # Mostrar estadísticas
        if loaded_count == total_count:
            self.stdout.write(self.style.SUCCESS(f'🎉 Todas las variables están configuradas ({loaded_count}/{total_count})'))
        elif loaded_count > 0:
            self.stdout.write(self.style.WARNING(f'⚠️  Algunas variables están configuradas ({loaded_count}/{total_count})'))
        else:
            self.stdout.write(self.style.ERROR('❌ Ninguna variable del .env está configurada correctamente'))

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
            self.stdout.write('   • Asegúrate de actualizar los valores de ejemplo (your-email@gmail.com, etc.)')
            self.stdout.write('   • Reinicia el servidor después de cambiar el .env')

        self.stdout.write('   • No subas el archivo .env al repositorio')
        self.stdout.write('   • Usa .env.example como plantilla')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🔍 Verificación completada!'))

    def _detect_environment(self, settings_module):
        """Detecta el entorno basándose en DJANGO_SETTINGS_MODULE"""
        if 'production' in settings_module:
            return 'production'
        elif 'staging' in settings_module:
            return 'staging'
        else:
            return 'development'

    def _get_environment_vars(self, environment):
        """Retorna las variables específicas para cada entorno"""
        if environment == 'production':
            return {
                'PRODUCTION_DOMAIN': 'Dominio de producción',
                'ALLOWED_HOSTS_PROD': 'Hosts permitidos en producción',
                'CSRF_TRUSTED_ORIGINS_PROD': 'Orígenes CSRF de confianza (producción)',
            }
        elif environment == 'staging':
            return {
                'STAGING_DOMAIN': 'Dominio de staging',
                'ALLOWED_HOSTS_STAGING': 'Hosts permitidos en staging',
                'CSRF_TRUSTED_ORIGINS_STAGING': 'Orígenes CSRF de confianza (staging)',
            }
        else:  # development
            return {
                'DOMAIN': 'Dominio de desarrollo',
                'ALLOWED_HOSTS_DEV': 'Hosts permitidos en desarrollo',
                'CSRF_TRUSTED_ORIGINS_DEV': 'Orígenes CSRF de confianza (desarrollo)',
            }

    def _load_example_values(self):
        """Lee el archivo .env.example y retorna un diccionario con los valores de ejemplo"""
        example_values = {}
        env_example_path = os.path.join(settings.BASE_DIR, '.env.example')

        if os.path.exists(env_example_path):
            try:
                with open(env_example_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            # Remover comillas si existen
                            value = value.strip().strip('"').strip("'")
                            example_values[key] = value
            except Exception as e:
                pass

        return example_values

    def _check_security_warning(self, var_name, value):
        """Verifica si hay advertencias de seguridad para una variable"""
        # DEBUG=True en producción/staging es un problema de seguridad
        if var_name == 'DEBUG':
            settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', '')
            if value.lower() == 'true' and ('production' in settings_module or 'staging' in settings_module):
                return '(⚠️ DEBUG=True no debe usarse en producción)'

        return None

    def _is_placeholder_value(self, var_name, current_value, example_value):
        """Determina si un valor es un placeholder que debe ser actualizado"""
        if not example_value:
            return False

        # Remover comillas del valor actual para comparación
        current_clean = current_value.strip().strip('"').strip("'")
        example_clean = example_value.strip().strip('"').strip("'")

        # Lista de valores válidos que NO son placeholders (aunque estén en .env.example)
        valid_values = [
            'smtp.gmail.com',  # Servidor real de Gmail
            'localhost',       # Válido para desarrollo
            '127.0.0.1',       # Válido para desarrollo
            '0.0.0.0',         # Válido para desarrollo
            'True',            # Booleano válido
            'False',           # Booleano válido
        ]

        # Si el valor está en la lista de valores válidos, no es placeholder
        for valid in valid_values:
            if current_clean.lower() == valid.lower():
                return False

        # Si el valor actual es exactamente igual al de ejemplo, verificar si es placeholder
        if current_clean == example_clean:
            # Solo marcar como placeholder si contiene patrones de ejemplo
            placeholder_indicators = [
                'your-',
                'yourdomain',
                'your domain',
                'example',
                'Mi Portfolio',  # Nombre genérico de proyecto
            ]

            for indicator in placeholder_indicators:
                if indicator.lower() in current_clean.lower():
                    return True

        # Lista de patrones específicos que son placeholders
        placeholder_patterns = [
            'your-email@gmail.com',
            'your-16-character-app-password',
            'your-app-password',
            'yourdomain.com',
            'your-domain.com',
        ]

        # Si el valor contiene algún patrón de placeholder
        for pattern in placeholder_patterns:
            if pattern.lower() in current_clean.lower():
                return True

        return False