from django.conf import settings
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType
from ..models import SiteConfiguration, AutoTranslationRecord


class EditingLanguageContextMixin:
    """Provide editing language context and helper notice for admin forms."""

    def _get_editing_language_payload(self):
        config = SiteConfiguration.get_solo()
        editing_code = config.default_language or settings.LANGUAGE_CODE
        language_map = dict(settings.LANGUAGES)
        editing_label = language_map.get(editing_code, editing_code.upper())
        target_codes = config.get_target_languages()
        target_labels = [language_map.get(code, code.upper()) for code in target_codes]
        return editing_code, editing_label, target_labels, target_codes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        editing_code, editing_label, target_labels, target_codes = self._get_editing_language_payload()
        context.setdefault('editing_language_code', editing_code)
        context.setdefault('editing_language_label', editing_label)
        context.setdefault('target_language_labels', target_labels)
        context.setdefault('current_language', editing_code)
        context.setdefault('default_language', editing_code)
        context.setdefault('available_languages', settings.LANGUAGES)
        context.setdefault('target_languages', target_codes)
        context.setdefault('settings_url', reverse('portfolio:admin-site-configuration'))
        return context


class AutoTranslationStatusMixin(EditingLanguageContextMixin):
    """Provide auto translation records in context for update views."""

    def get_auto_translation_records(self):
        obj = getattr(self, 'object', None)
        if obj is None or obj.pk is None:
            return []
        content_type = ContentType.objects.get_for_model(obj.__class__)
        return AutoTranslationRecord.objects.filter(
            content_type=content_type,
            object_id=obj.pk
        ).order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auto_translation_records' not in context:
            context['auto_translation_records'] = self.get_auto_translation_records()
        config = SiteConfiguration.get_solo()
        context['auto_translation_enabled'] = config.auto_translate_enabled
        context['default_language'] = config.default_language
        context['target_languages'] = config.get_target_languages()
        return context


def _build_translation_status_map(model, objects):
    """Build a per-object translation status overview for dashboard tables."""
    items = list(objects)
    config = SiteConfiguration.get_solo()
    if not items:
        default_language = config.default_language or settings.LANGUAGE_CODE
        return items, {}, config.auto_translate_enabled, default_language
    default_language = config.default_language or settings.LANGUAGE_CODE
    target_languages = [code for code in config.get_target_languages() if code != default_language]
    languages = [default_language] + target_languages
    language_labels = dict(settings.LANGUAGES)

    content_type = ContentType.objects.get_for_model(model)
    object_ids = [item.pk for item in items if item.pk]
    records = AutoTranslationRecord.objects.filter(
        content_type=content_type,
        object_id__in=object_ids,
    )

    record_map = {}
    for record in records:
        record_map.setdefault(record.object_id, {})[record.language_code] = record

    status_map = {}
    for item in items:
        if (
            hasattr(item, '_prefetched_objects_cache')
            and 'translations' in item._prefetched_objects_cache
        ):
            translations_qs = item._prefetched_objects_cache['translations']
            translation_codes = {trans.language_code for trans in translations_qs}
        else:
            translation_codes = set(item.translations.values_list('language_code', flat=True))

        entry_list = []
        for code in languages:
            label = language_labels.get(code, code.upper())
            entry = {
                'code': code.upper(),
                'label': label,
                'role': 'base' if code == default_language else 'target',
            }

            if code == default_language:
                if code in translation_codes:
                    entry['state'] = 'ok'
                    entry['tooltip'] = _('%(language)s content ready (base)') % {'language': label}
                else:
                    entry['state'] = 'missing'
                    entry['tooltip'] = _('%(language)s content missing (base)') % {'language': label}
            else:
                record = record_map.get(item.pk, {}).get(code)
                if code in translation_codes:
                    entry['state'] = 'ok'
                    entry['tooltip'] = _('%(language)s translation ready') % {'language': label}
                elif record:
                    entry['record_status'] = record.status
                    if record.status == AutoTranslationRecord.STATUS_FAILED:
                        entry['state'] = 'failed'
                        error = (record.error_message or '')[:160]
                        if error:
                            entry['tooltip'] = _('%(language)s auto-translation failed: %(error)s') % {
                                'language': label,
                                'error': error,
                            }
                        else:
                            entry['tooltip'] = _('%(language)s auto-translation failed') % {'language': label}
                    elif record.status == AutoTranslationRecord.STATUS_PENDING:
                        entry['state'] = 'pending'
                        entry['tooltip'] = _('%(language)s auto-translation pending') % {'language': label}
                    else:
                        entry['state'] = 'missing'
                        entry['tooltip'] = _('%(language)s translation missing') % {'language': label}
                else:
                    entry['state'] = 'missing'
                    entry['tooltip'] = _('%(language)s translation missing') % {'language': label}
            entry_list.append(entry)

        status_map[item.pk] = entry_list

    return items, status_map, config.auto_translate_enabled, default_language
