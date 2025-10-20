import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from parler.signals import post_translation_save

from .models import Profile, Project, BlogPost, Experience, Education
from .translation import schedule_auto_translation

logger = logging.getLogger(__name__)


def _handle_auto_translation(instance, **kwargs):
    raw = kwargs.get('raw', False)
    created = kwargs.get('created', False)

    logger.info(
        f"post_save signal: {instance.__class__.__name__} pk={instance.pk}, "
        f"created={created}, raw={raw}"
    )

    if raw:
        logger.debug(f"Skipping translation for {instance.__class__.__name__} pk={instance.pk} (raw=True)")
        return

    if instance.pk is None:
        logger.warning(f"Instance {instance.__class__.__name__} has pk=None, skipping translation")
        return

    schedule_auto_translation(instance)


def _handle_translation_saved(sender, instance, **kwargs):
    """
    Handle parler's post_translation_save signal.
    This fires AFTER parler saves the translation, ensuring content is available.

    IMPORTANT: Only trigger auto-translation when saving the DEFAULT language.
    This prevents infinite loops where translating to Spanish triggers another translation.
    """
    language_code = instance.language_code if hasattr(instance, 'language_code') else None
    master = instance.master if hasattr(instance, 'master') else None

    if master is None:
        logger.warning(f"post_translation_save: no master instance found")
        return

    # Get the default language from settings
    from django.conf import settings
    from .models import SiteConfiguration

    config = SiteConfiguration.get_solo()
    default_language = config.default_language or settings.LANGUAGE_CODE

    logger.info(
        f"post_translation_save signal: {master.__class__.__name__} pk={master.pk}, "
        f"language={language_code}, default={default_language}"
    )

    # CRITICAL: Only schedule translation if we're saving the DEFAULT language
    # This prevents infinite loops where saving ES translation triggers another translation
    if language_code != default_language:
        logger.debug(
            f"Skipping auto-translation: saved language '{language_code}' is not default '{default_language}'"
        )
        return

    # Schedule translation after the transaction commits
    schedule_auto_translation(master)


# Use post_translation_save for all parler models (fires after translation is saved)
# Note: The sender for post_translation_save is the Translation model, not the master model
@receiver(post_translation_save)
def auto_translate_on_translation_save(sender, instance, **kwargs):
    """
    Universal handler for all translatable models.
    Fires when ANY translation is saved via parler.
    """
    # Get the master instance (the actual model like BlogPost, Project, etc.)
    master = getattr(instance, 'master', None)

    if master is None:
        return

    # Only handle our translatable models
    if not isinstance(master, (Profile, Project, BlogPost, Experience, Education)):
        return

    _handle_translation_saved(sender, instance, **kwargs)
