"""
Utilities to trigger automatic translations for translatable models.
"""
import logging
from typing import Dict, Tuple, Type

from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import transaction
from django.utils import translation as django_translation
from django.core.exceptions import ImproperlyConfigured

from .models import (
    SiteConfiguration,
    AutoTranslationRecord,
    Profile,
    Project,
    BlogPost,
    Experience,
    Education,
)
from .services.translation_service import TranslationError

logger = logging.getLogger(__name__)

# field_name -> format (text/html)
AutoFields = Dict[str, str]

AUTO_TRANSLATABLE_MODELS: Dict[Type, AutoFields] = {
    Profile: {
        'name': 'text',
        'title': 'text',
        'bio': 'html',
        'location': 'text',
    },
    Project: {
        'title': 'text',
        'description': 'text',
        'detailed_description': 'html',
    },
    BlogPost: {
        'title': 'text',
        'content': 'text',
        'excerpt': 'text',
    },
    Experience: {
        'company': 'text',
        'position': 'text',
        'description': 'html',
    },
    Education: {
        'institution': 'text',
        'degree': 'text',
        'field_of_study': 'text',
        'description': 'html',
    },
}


def schedule_auto_translation(instance):
    """Schedule translation after the current transaction commits."""
    model = instance.__class__
    if model not in AUTO_TRANSLATABLE_MODELS:
        logger.debug(f"Model {model.__name__} not in AUTO_TRANSLATABLE_MODELS")
        return

    config = SiteConfiguration.get_solo()
    if not config.auto_translate_enabled:
        logger.debug(f"Auto translation disabled in config for {model.__name__} pk={instance.pk}")
        return

    source_language = getattr(instance, 'get_current_language', lambda: None)() or config.default_language
    default_language = config.default_language or settings.LANGUAGE_CODE

    logger.info(
        f"Scheduling translation for {model.__name__} pk={instance.pk}, "
        f"source_lang={source_language}, default_lang={default_language}"
    )

    if source_language != default_language:
        # Only translate when content is saved in default language
        logger.debug(
            f"Skipping translation for {model.__name__} pk={instance.pk}: "
            f"source language {source_language} != default {default_language}"
        )
        return

    pk = instance.pk
    logger.info(f"Translation scheduled via transaction.on_commit for {model.__name__} pk={pk}")
    transaction.on_commit(lambda: _run_auto_translation(model, pk, source_language))


def _run_auto_translation(model: Type, pk: int, source_language: str):
    logger.info(f"_run_auto_translation called for {model.__name__} pk={pk}, source_lang={source_language}")

    try:
        instance = model.objects.get(pk=pk)
    except model.DoesNotExist:
        logger.warning(f"Instance {model.__name__} pk={pk} not found for translation")
        return

    # Log current language and available translations
    current_lang = getattr(instance, 'get_current_language', lambda: None)()
    available_langs = getattr(instance, 'get_available_languages', lambda: [])()
    logger.info(
        f"Instance {model.__name__} pk={pk}: current_lang={current_lang}, "
        f"available_langs={available_langs}, source_lang={source_language}"
    )

    config = SiteConfiguration.get_solo()
    if not config.auto_translate_enabled:
        logger.debug(f"Auto translation disabled, skipping {model.__name__} pk={pk}")
        return

    try:
        service = config.get_translation_service()
    except ImproperlyConfigured as exc:
        logger.warning("Auto translation skipped (config incomplete): %s", exc)
        return

    fields = AUTO_TRANSLATABLE_MODELS.get(model, {})
    if not fields:
        logger.warning(f"No translatable fields configured for {model.__name__}")
        return

    # gather source data
    source_data: Dict[str, Tuple[str, str]] = {}
    for field, fmt in fields.items():
        value = instance.safe_translation_getter(field, language_code=source_language, any_language=False)
        if value:
            source_data[field] = (value, fmt)
            logger.debug(f"  - Field '{field}' has content ({len(value)} chars)")
        else:
            logger.debug(f"  - Field '{field}' is empty")

    if not source_data:
        logger.info(f"No source data to translate for {model.__name__} pk={pk} in language {source_language}")
        return

    translation_model = instance.translations.model
    content_type = ContentType.objects.get_for_model(model)
    target_languages = config.get_target_languages()

    logger.info(f"Will translate {model.__name__} pk={pk} to target languages: {target_languages}")

    for target_language in target_languages:
        _translate_language(
            instance=instance,
            translation_model=translation_model,
            content_type=content_type,
            service=service,
            source_language=source_language,
            target_language=target_language,
            source_data=source_data,
        )


def _translate_language(
    instance,
    translation_model,
    content_type: ContentType,
    service,
    source_language: str,
    target_language: str,
    source_data: Dict[str, Tuple[str, str]],
):
    logger.info(
        f"_translate_language: {instance.__class__.__name__} pk={instance.pk}, "
        f"{source_language} -> {target_language}"
    )

    if source_language == target_language:
        logger.debug(f"Skipping same language: {source_language}")
        return

    record = AutoTranslationRecord.objects.filter(
        content_type=content_type,
        object_id=instance.pk,
        language_code=target_language,
    ).first()

    try:
        existing_translation = translation_model.objects.get(
            master_id=instance.pk,
            language_code=target_language,
        )
        logger.debug(f"  - Existing translation found for {target_language}")
    except translation_model.DoesNotExist:
        existing_translation = None
        logger.debug(f"  - No existing translation for {target_language}")

    if record and not record.auto_generated:
        # Respect manual translations explicitly marked
        logger.info(
            f"Skipping auto translation for {instance.__class__.__name__} pk={instance.pk} "
            f"lang={target_language} (manual override - record.auto_generated=False)"
        )
        return

    total_duration = 0
    translated_fields = {}

    logger.info(f"  - Translating {len(source_data)} fields: {list(source_data.keys())}")

    for field, (value, fmt) in source_data.items():
        try:
            logger.debug(f"  - Translating field '{field}' ({len(value)} chars, format={fmt})")
            result = service.translate(value, source_language, target_language, format='html' if fmt == 'html' else 'text')
            logger.debug(f"  - Field '{field}' translated successfully in {result.duration_ms}ms")
        except TranslationError as exc:
            _mark_translation_failure(record, content_type, instance.pk, target_language, source_language, str(exc))
            logger.exception("Translation error on %s field %s -> %s: %s", instance.__class__.__name__, field, target_language, exc)
            return
        except Exception as exc:  # noqa: BLE001
            _mark_translation_failure(record, content_type, instance.pk, target_language, source_language, str(exc))
            logger.exception("Unexpected translation failure: %s", exc)
            return
        else:
            translated_fields[field] = result.translated_text
            total_duration += result.duration_ms

    if not translated_fields:
        logger.warning(f"No fields were translated for {instance.__class__.__name__} pk={instance.pk}, lang={target_language}")
        return

    # upsert translation
    logger.info(f"  - Saving translation to DB for {target_language}")
    translation_model.objects.update_or_create(
        master=instance,
        language_code=target_language,
        defaults=translated_fields,
    )

    record_defaults = {
        'source_language': source_language,
    }
    record, _created = AutoTranslationRecord.objects.update_or_create(
        content_type=content_type,
        object_id=instance.pk,
        language_code=target_language,
        defaults=record_defaults,
    )
    record.provider = service.provider
    record.duration_ms = total_duration
    record.auto_generated = True
    record.status = AutoTranslationRecord.STATUS_SUCCESS
    record.error_message = ''
    record.save(update_fields=['provider', 'duration_ms', 'auto_generated', 'status', 'error_message'])

    logger.info(
        f"  - Translation SUCCESS: {instance.__class__.__name__} pk={instance.pk}, "
        f"lang={target_language}, duration={total_duration}ms, record_created={_created}"
    )


def _mark_translation_failure(record, content_type, object_id, target_language, source_language, message: str):
    record = record or AutoTranslationRecord(
        content_type=content_type,
        object_id=object_id,
        language_code=target_language,
        source_language=source_language,
    )
    record.auto_generated = False
    record.provider = ''
    record.duration_ms = 0
    record.status = AutoTranslationRecord.STATUS_FAILED
    record.error_message = message[:1000]
    record.save()
