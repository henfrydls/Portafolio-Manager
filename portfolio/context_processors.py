from .models import Profile

def profile_context(request):
    """
    Context processor para hacer el perfil disponible en todos los templates
    """
    try:
        profile = Profile.objects.first()
    except Profile.DoesNotExist:
        profile = None
    
    return {
        'profile': profile
    }