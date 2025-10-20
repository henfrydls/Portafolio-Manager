from datetime import date
from unittest.mock import patch

from django.test import TestCase

from portfolio.models import SiteConfiguration, Experience, AutoTranslationRecord
from portfolio.translation import _run_auto_translation
from portfolio.services.translation_service import TranslationResult, TranslationError


class AutoTranslationServiceTests(TestCase):
    def setUp(self):
        config = SiteConfiguration.get_solo()
        config.default_language = 'en'
        config.auto_translate_enabled = True
        config.translation_provider = 'libretranslate'
        config.translation_api_url = 'http://mock-translate.local'
        config.translation_timeout = 5
        config.save()

    def _create_experience(self):
        experience = Experience()
        experience.set_current_language('en')
        experience.company = "ACME Inc."
        experience.position = "Senior Engineer"
        experience.description = "Responsible for designing scalable systems."
        experience.start_date = date(2021, 1, 1)
        experience.current = True
        experience.save()
        return experience

    def test_successful_auto_translation_creates_record(self):
        experience = self._create_experience()

        class DummyService:
            provider = 'libretranslate'

            def translate(self, text, source, target, **kwargs):
                return TranslationResult(
                    translated_text=f"{text} ({target})",
                    provider='libretranslate',
                    duration_ms=25,
                )

        with patch('portfolio.models.SiteConfiguration.get_translation_service') as mock_service:
            mock_service.return_value = DummyService()
            _run_auto_translation(Experience, experience.pk, 'en')

        translated = Experience.objects.language('es').get(pk=experience.pk)
        self.assertIn('(es)', translated.company)
        record = AutoTranslationRecord.objects.get(object_id=experience.pk, language_code='es')
        self.assertEqual(record.status, AutoTranslationRecord.STATUS_SUCCESS)
        self.assertTrue(record.auto_generated)

    def test_failed_translation_creates_failure_record(self):
        experience = self._create_experience()

        class FailingService:
            provider = 'libretranslate'

            def translate(self, *args, **kwargs):
                raise TranslationError("Service unavailable")

        with patch('portfolio.models.SiteConfiguration.get_translation_service') as mock_service:
            mock_service.return_value = FailingService()
            _run_auto_translation(Experience, experience.pk, 'en')

        record = AutoTranslationRecord.objects.get(object_id=experience.pk, language_code='es')
        self.assertEqual(record.status, AutoTranslationRecord.STATUS_FAILED)
        self.assertFalse(record.auto_generated)
        self.assertIn('Service unavailable', record.error_message)
