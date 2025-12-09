from django.contrib import admin
from ..models import Contact, PageVisit, AutoTranslationRecord


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Administración de mensajes de contacto"""
    list_display = ('name', 'email', 'subject', 'created_at', 'read', 'message_preview')
    list_filter = ('read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    def message_preview(self, obj):
        """Muestra preview del mensaje"""
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = "Vista previa del mensaje"
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        """Acción para marcar mensajes como leídos"""
        updated = queryset.update(read=True)
        self.message_user(request, f'{updated} mensajes marcados como leídos.')
    mark_as_read.short_description = "Marcar como leído"
    
    def mark_as_unread(self, request, queryset):
        """Acción para marcar mensajes como no leídos"""
        updated = queryset.update(read=False)
        self.message_user(request, f'{updated} mensajes marcados como no leídos.')
    mark_as_unread.short_description = "Marcar como no leído"
    
    def has_add_permission(self, request):
        """No permitir agregar mensajes desde el admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Solo permitir marcar como leído/no leído"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Permitir eliminar mensajes"""
        return True


@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    """Administración de visitas de páginas"""
    list_display = ('page_url', 'page_title', 'timestamp', 'ip_address', 'user_agent_preview')
    list_filter = ('timestamp', 'page_url')
    search_fields = ('page_url', 'page_title', 'ip_address')
    readonly_fields = ('page_url', 'page_title', 'timestamp', 'ip_address', 'user_agent')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    def user_agent_preview(self, obj):
        """Muestra preview del user agent"""
        return obj.user_agent[:50] + "..." if len(obj.user_agent) > 50 else obj.user_agent
    user_agent_preview.short_description = "User Agent"
    
    def has_add_permission(self, request):
        """No permitir agregar visitas desde el admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir editar visitas"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Permitir eliminar visitas para limpieza"""
        return True
    
    actions = ['delete_old_visits']
    
    def delete_old_visits(self, request, queryset):
        """Acción para eliminar visitas antiguas (más de 6 meses)"""
        from django.utils import timezone
        from datetime import timedelta
        
        six_months_ago = timezone.now() - timedelta(days=180)
        old_visits = PageVisit.objects.filter(timestamp__lt=six_months_ago)
        count = old_visits.count()
        old_visits.delete()
        
        self.message_user(request, f'{count} visitas antiguas eliminadas.')
    delete_old_visits.short_description = "Eliminar visitas antiguas (>6 meses)"


@admin.register(AutoTranslationRecord)
class AutoTranslationRecordAdmin(admin.ModelAdmin):
    """Registro de traducciones automáticas."""
    list_display = (
        'content_object', 'language_code', 'source_language',
        'provider', 'auto_generated', 'status', 'updated_at',
    )
    list_filter = (
        'status', 'auto_generated', 'language_code',
        'source_language', 'provider', 'content_type',
    )
    search_fields = (
        'object_id', 'language_code', 'source_language',
        'provider', 'error_message',
    )
    readonly_fields = (
        'content_type', 'object_id', 'language_code', 'source_language',
        'provider', 'duration_ms', 'auto_generated', 'status',
        'error_message', 'created_at', 'updated_at',
    )
    ordering = ('-updated_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# Personalización del sitio de administración / Admin site customization
admin.site.site_header = "Portfolio Administration / Administración del Portafolio"
admin.site.site_title = "Portfolio Admin"
admin.site.index_title = "Portfolio Management Panel / Panel de Gestión del Portafolio"
