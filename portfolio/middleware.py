from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from django.conf import settings
from .models import PageVisit
import logging

logger = logging.getLogger(__name__)


class PageVisitMiddleware(MiddlewareMixin):
    """
    Middleware para registrar visitas a páginas del sitio web.
    
    Registra información básica de cada visita incluyendo:
    - URL de la página visitada
    - Título de la página (si está disponible)
    - Timestamp de la visita
    - Dirección IP del visitante
    - User Agent del navegador
    
    Excluye automáticamente:
    - Rutas de administración (/admin/)
    - Archivos estáticos (/static/)
    - Archivos media (/media/)
    - APIs internas
    - Bots conocidos (opcional)
    """
    
    # URLs que se excluyen del tracking
    EXCLUDED_PATHS = [
        '/admin/',
        '/static/',
        '/media/',
        '/favicon.ico',
        '/robots.txt',
        '/sitemap.xml',
        '/.well-known/',  # Excluir todas las rutas .well-known
        '/apple-touch-icon',
        '/browserconfig.xml',
        '/manifest.json',
        '/api/',  # Excluir todas las URLs de API
        '/manage/ajax/',  # Excluir llamadas AJAX del admin
        
        # Páginas de administración del portfolio
        '/dashboard/',
        '/analytics/',
        '/admin-dashboard/',  # Ruta alternativa de dashboard
        '/admin-analytics/',  # Ruta alternativa de analytics
        '/login/',
        '/logout/',
        '/password-change/',
        '/manage/',  # Excluir todas las rutas de gestión (/manage/*)
    ]
    
    # Patrones de URL que se excluyen (para requests automáticos)
    EXCLUDED_PATTERNS = [
        '.well-known',
        'devtools',
        'chrome-extension',
        'moz-extension',
        'safari-extension',
        'edge-extension',
        '__webpack',
        'hot-update',
        '.map',
        'sourcemap',
    ]
    
    # User agents de bots conocidos que se excluyen
    BOT_USER_AGENTS = [
        'googlebot',
        'bingbot',
        'slurp',
        'duckduckbot',
        'baiduspider',
        'yandexbot',
        'facebookexternalhit',
        'linkedinbot',
        'whatsapp',
        'telegram',
        'bot',
        'crawler',
        'spider',
        'scraper',
        'curl',
        'wget',
        'python-requests',
        'postman',
        'insomnia',
        'httpie',
    ]
    
    # Patrones de User Agent que indican herramientas de desarrollo
    DEV_TOOL_PATTERNS = [
        'devtools',
        'chrome-devtools',
        'webkit-devtools',
        'firefox-devtools',
        'safari-devtools',
        'edge-devtools',
        'vscode',
        'jetbrains',
        'intellij',
    ]
    
    def process_request(self, request):
        """
        Procesa cada request para determinar si debe ser registrado.
        """
        # Solo registrar requests GET (páginas visitadas)
        if request.method != 'GET':
            return None
            
        # Obtener la ruta de la URL
        path = request.path
        
        # Verificar si la ruta debe ser excluida
        if self._should_exclude_path(path):
            return None
            
        # Verificar si es un bot conocido
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if self._is_bot(user_agent):
            return None
            
        # Obtener información del request
        ip_address = self._get_client_ip(request)
        
        # Intentar resolver la URL para obtener información adicional
        try:
            resolved = resolve(path)
            view_name = resolved.view_name
        except:
            view_name = 'unknown'
        
        # Generar título de página basado en la URL
        page_title = self._generate_page_title(path, view_name)
        
        # Registrar la visita de forma asíncrona para no afectar el rendimiento
        try:
            PageVisit.objects.create(
                page_url=path,
                page_title=page_title,
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]  # Limitar longitud
            )
        except Exception as e:
            # Log del error pero no interrumpir el request
            logger.error(f"Error registrando visita: {e}")
        
        return None
    
    def _should_exclude_path(self, path):
        """
        Determina si una ruta debe ser excluida del tracking.
        """
        # Verificar rutas exactas y prefijos
        for excluded_path in self.EXCLUDED_PATHS:
            if path.startswith(excluded_path):
                return True
        
        # Verificar patrones en la URL completa
        path_lower = path.lower()
        for pattern in self.EXCLUDED_PATTERNS:
            if pattern in path_lower:
                return True
        
        return False
    
    def _is_bot(self, user_agent):
        """
        Determina si el user agent corresponde a un bot conocido o herramienta de desarrollo.
        """
        # Verificar bots conocidos
        for bot in self.BOT_USER_AGENTS:
            if bot in user_agent:
                return True
        
        # Verificar herramientas de desarrollo
        for dev_pattern in self.DEV_TOOL_PATTERNS:
            if dev_pattern in user_agent:
                return True
        
        # Verificar si el user agent está vacío o es muy corto (posible bot)
        if not user_agent or len(user_agent.strip()) < 10:
            return True
        
        return False
    
    def _get_client_ip(self, request):
        """
        Obtiene la dirección IP real del cliente, considerando proxies.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Tomar la primera IP si hay múltiples (cadena de proxies)
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        
        return ip
    
    def _generate_page_title(self, path, view_name):
        """
        Genera un título descriptivo para la página basado en la URL y vista.
        """
        # Mapeo de rutas a títulos descriptivos
        title_mapping = {
            '/': 'Página Principal',
            '/projects/': 'Lista de Proyectos',
            '/resume/': 'Currículum',
            '/blog/': 'Blog',
            '/contact/': 'Contacto',
        }
        
        # Verificar mapeo directo
        if path in title_mapping:
            return title_mapping[path]
        
        # Generar título basado en patrones de URL
        if path.startswith('/projects/') and path != '/projects/':
            return 'Detalle de Proyecto'
        elif path.startswith('/blog/') and path != '/blog/':
            return 'Post del Blog'
        elif any(admin_path in path for admin_path in ['/admin/', '/dashboard/', '/analytics/', '/manage/', '/login/']):
            return 'Administración'
        
        # Título basado en el nombre de la vista
        if view_name and view_name != 'unknown':
            # Convertir nombres de vista a títulos legibles
            view_title_mapping = {
                'home': 'Página Principal',
                'project-list': 'Lista de Proyectos',
                'project-detail': 'Detalle de Proyecto',
                'resume': 'Currículum',
                'blog-list': 'Blog',
                'blog-detail': 'Post del Blog',
                'contact': 'Contacto',
            }
            return view_title_mapping.get(view_name, view_name.replace('-', ' ').title())
        
        # Título por defecto
        return f"Página: {path}"
    
    @classmethod
    def cleanup_invalid_visits(cls):
        """
        Método para limpiar visitas inválidas ya registradas.
        Puede ser ejecutado manualmente desde el shell de Django.
        """
        from django.db.models import Q
        
        # Construir query para visitas inválidas
        invalid_conditions = Q()
        
        # Agregar condiciones para rutas excluidas
        for excluded_path in cls.EXCLUDED_PATHS:
            invalid_conditions |= Q(page_url__startswith=excluded_path)
        
        # Agregar condiciones para patrones excluidos
        for pattern in cls.EXCLUDED_PATTERNS:
            invalid_conditions |= Q(page_url__icontains=pattern)
        
        # Agregar condiciones para user agents de bots
        for bot in cls.BOT_USER_AGENTS:
            invalid_conditions |= Q(user_agent__icontains=bot)
        
        # Agregar condiciones para herramientas de desarrollo
        for dev_pattern in cls.DEV_TOOL_PATTERNS:
            invalid_conditions |= Q(user_agent__icontains=dev_pattern)
        
        # Ejecutar limpieza
        try:
            deleted_count, _ = PageVisit.objects.filter(invalid_conditions).delete()
            logger.info(f"Limpieza manual: {deleted_count} visitas inválidas eliminadas")
            return deleted_count
        except Exception as e:
            logger.error(f"Error en limpieza manual de visitas inválidas: {e}")
            return 0


class PageVisitCleanupMiddleware(MiddlewareMixin):
    """
    Middleware opcional para limpieza automática de visitas antiguas.
    
    Ejecuta limpieza periódica de registros de visitas más antiguos
    que el período configurado (por defecto 6 meses).
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.cleanup_counter = 0
        # Ejecutar limpieza cada 1000 requests
        self.cleanup_frequency = getattr(settings, 'PAGE_VISIT_CLEANUP_FREQUENCY', 1000)
        # Mantener visitas de los últimos 6 meses por defecto
        self.retention_days = getattr(settings, 'PAGE_VISIT_RETENTION_DAYS', 180)
    
    def process_request(self, request):
        """
        Ejecuta limpieza periódica de visitas antiguas.
        """
        self.cleanup_counter += 1
        
        if self.cleanup_counter >= self.cleanup_frequency:
            self.cleanup_counter = 0
            self._cleanup_old_visits()
        
        return None
    
    def _cleanup_old_visits(self):
        """
        Elimina visitas más antiguas que el período de retención.
        """
        try:
            from django.utils import timezone
            from datetime import timedelta
            
            cutoff_date = timezone.now() - timedelta(days=self.retention_days)
            deleted_count, _ = PageVisit.objects.filter(timestamp__lt=cutoff_date).delete()
            
            if deleted_count > 0:
                logger.info(f"Limpieza automática: {deleted_count} visitas antiguas eliminadas")
                
        except Exception as e:
            logger.error(f"Error en limpieza automática de visitas: {e}")