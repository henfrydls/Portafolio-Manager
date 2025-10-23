"""
Django management command to auto-translate .po files using LibreTranslate.

Usage:
    python manage.py translate_po --locale es
    python manage.py translate_po --locale es --dry-run
    python manage.py translate_po --locale es --force
"""
import re
import os
from typing import List, Tuple, Dict
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from portfolio.models import SiteConfiguration
from portfolio.services.translation_service import TranslationError


class Command(BaseCommand):
    help = 'Automatically translate empty msgstr entries in .po files using LibreTranslate'

    def add_arguments(self, parser):
        parser.add_argument(
            '--locale',
            type=str,
            default='es',
            help='Target locale to translate (default: es)',
        )
        parser.add_argument(
            '--domain',
            type=str,
            default='django',
            help='Translation domain (default: django)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be translated without modifying files',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-translate all entries, even non-empty ones',
        )
        parser.add_argument(
            '--source-lang',
            type=str,
            default='en',
            help='Source language (default: en)',
        )

    def handle(self, *args, **options):
        locale = options['locale']
        domain = options['domain']
        dry_run = options['dry_run']
        force = options['force']
        source_lang = options['source_lang']

        # Build path to .po file
        locale_dir = os.path.join(settings.BASE_DIR, 'locale', locale, 'LC_MESSAGES')
        po_file_path = os.path.join(locale_dir, f'{domain}.po')

        if not os.path.exists(po_file_path):
            raise CommandError(f'.po file not found: {po_file_path}')

        self.stdout.write(self.style.SUCCESS(f'\n=== Auto-Translation Tool ==='))
        self.stdout.write(f'File: {po_file_path}')
        self.stdout.write(f'Source: {source_lang} -> Target: {locale}')
        self.stdout.write(f'Mode: {"DRY RUN" if dry_run else "LIVE"}')
        if force:
            self.stdout.write(self.style.WARNING('Force mode: Will re-translate all entries'))
        self.stdout.write('')

        # Get translation service
        try:
            config = SiteConfiguration.get_solo()
            translation_service = config.get_translation_service()
            self.stdout.write(self.style.SUCCESS(f'✓ Translation service ready: {translation_service.provider}'))
            self.stdout.write(f'  API URL: {translation_service.api_url}')
        except Exception as e:
            raise CommandError(f'Failed to initialize translation service: {e}')

        # Read .po file
        self.stdout.write('\n📖 Reading .po file...')
        with open(po_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse and translate
        entries = self._parse_po_file(content)
        self.stdout.write(f'  Found {len(entries)} translation entries')

        # Filter entries that need translation
        to_translate = [
            entry for entry in entries
            if force or not entry['msgstr'] or entry['msgstr'] == '""'
        ]

        self.stdout.write(f'  {len(to_translate)} entries need translation')

        if not to_translate:
            self.stdout.write(self.style.SUCCESS('\n✓ All entries already translated!'))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING('\n🔍 DRY RUN - Showing first 10 entries that would be translated:'))
            for i, entry in enumerate(to_translate[:10]):
                msgid = entry['msgid'].strip('"')
                self.stdout.write(f'\n{i+1}. msgid: {msgid[:80]}...' if len(msgid) > 80 else f'\n{i+1}. msgid: {msgid}')
            self.stdout.write(f'\n... and {len(to_translate) - 10} more entries')
            return

        # Translate entries
        self.stdout.write(f'\n🚀 Starting translation of {len(to_translate)} entries...')
        translated_entries = self._translate_entries(
            to_translate,
            translation_service,
            source_lang,
            locale
        )

        # Update content with translations
        self.stdout.write('\n💾 Updating .po file...')
        updated_content = self._update_po_content(content, translated_entries)

        # Write updated file
        with open(po_file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully translated {len(translated_entries)} entries'))
        self.stdout.write(f'  Updated file: {po_file_path}')

        # Compile messages
        self.stdout.write('\n🔨 Compiling messages...')
        from django.core.management import call_command
        try:
            call_command('compilemessages', locale=[locale], verbosity=0)
            self.stdout.write(self.style.SUCCESS('✓ Messages compiled successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to compile messages: {e}'))

        self.stdout.write(self.style.SUCCESS('\n✅ Translation complete!\n'))

    def _parse_po_file(self, content: str) -> List[Dict]:
        """Parse .po file and extract msgid/msgstr pairs with their positions."""
        entries = []

        # Pattern to match msgid and msgstr (including multiline)
        # This regex captures: optional comments, msgid, and msgstr
        pattern = r'((?:#[^\n]*\n)*)(msgid\s+"[^"]*"(?:\n"[^"]*")*)\s*(msgstr\s+"[^"]*"(?:\n"[^"]*")*)'

        for match in re.finditer(pattern, content):
            comments = match.group(1)
            msgid_full = match.group(2)
            msgstr_full = match.group(3)

            # Extract the actual msgid text (first line only for simplicity)
            msgid_match = re.search(r'msgid\s+"([^"]*)"', msgid_full)
            msgstr_match = re.search(r'msgstr\s+"([^"]*)"', msgstr_full)

            if msgid_match:
                msgid = msgid_match.group(1)
                msgstr = msgstr_match.group(1) if msgstr_match else ''

                # Skip empty msgid (file header)
                if not msgid:
                    continue

                entries.append({
                    'comments': comments,
                    'msgid': f'"{msgid}"',
                    'msgstr': f'"{msgstr}"',
                    'msgid_full': msgid_full,
                    'msgstr_full': msgstr_full,
                    'start': match.start(),
                    'end': match.end(),
                })

        return entries

    def _translate_entries(
        self,
        entries: List[Dict],
        translation_service,
        source_lang: str,
        target_lang: str
    ) -> Dict[str, str]:
        """Translate entries and return mapping of msgid -> translated msgstr."""
        translations = {}
        total = len(entries)
        errors = 0

        for i, entry in enumerate(entries, 1):
            msgid = entry['msgid'].strip('"')

            # Skip if already cached
            if msgid in translations:
                continue

            # Progress indicator
            if i % 10 == 0 or i == total:
                self.stdout.write(f'  Progress: {i}/{total} ({int(i/total*100)}%)', ending='\r')

            try:
                result = translation_service.translate(
                    msgid,
                    source_lang,
                    target_lang,
                    format='text'
                )
                translations[msgid] = result.translated_text

            except TranslationError as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(f'\n  ✗ Error translating: {msgid[:50]}... - {e}')
                )
                # Keep original for failed translations
                translations[msgid] = msgid
            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(f'\n  ✗ Unexpected error: {msgid[:50]}... - {e}')
                )
                translations[msgid] = msgid

        self.stdout.write('')  # New line after progress

        if errors > 0:
            self.stdout.write(
                self.style.WARNING(f'  ⚠ {errors} translation errors encountered')
            )

        return translations

    def _update_po_content(self, content: str, translations: Dict[str, str]) -> str:
        """Update .po content with new translations."""

        def replace_msgstr(match):
            msgid_full = match.group(2)
            msgstr_full = match.group(3)

            # Extract msgid
            msgid_match = re.search(r'msgid\s+"([^"]*)"', msgid_full)
            if not msgid_match:
                return match.group(0)

            msgid = msgid_match.group(1)

            # Check if we have a translation
            if msgid in translations:
                translated = translations[msgid]
                # Escape quotes in translation
                translated = translated.replace('"', '\\"')
                new_msgstr = f'msgstr "{translated}"'
                return match.group(1) + match.group(2) + '\n' + new_msgstr

            return match.group(0)

        pattern = r'((?:#[^\n]*\n)*)(msgid\s+"[^"]*"(?:\n"[^"]*")*)\s*(msgstr\s+"[^"]*"(?:\n"[^"]*")*)'
        updated_content = re.sub(pattern, replace_msgstr, content)

        return updated_content
