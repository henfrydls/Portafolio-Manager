from django.utils import translation
from django.conf import settings
from .models import Profile, SiteConfiguration

def profile_context(request):
    """
    Context processor para hacer el perfil disponible en todos los templates
    """
    try:
        profile = Profile.get_solo()
        if profile:
            current_lang = translation.get_language() or getattr(settings, 'LANGUAGE_CODE', 'en')
            profile.set_current_language(current_lang)
    except Profile.DoesNotExist:
        profile = None
    
    try:
        site_config = SiteConfiguration.get_solo()
    except Exception:
        site_config = None
    
    return {
        'profile': profile,
        'site_config': site_config,
    }
