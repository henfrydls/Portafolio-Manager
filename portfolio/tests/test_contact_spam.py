"""
Anti-spam regression tests for the contact form.

These cover the holes that let a bot flood the inbox and relay scam
"confirmation" emails to third parties:

* reCAPTCHA was fail-open (skipped when no token was sent)
* the per-IP rate limit was disabled / never matched the form endpoint
* the auto-confirmation email was sent to attacker-supplied addresses
* the spam keyword filter ignored the subject and missed "btc"
* the honeypot timing check was dead code (field was never declared)
"""
import time
from unittest import mock

from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from portfolio.forms.contact import SecureContactFormWithHoneypot
from portfolio.models import Contact
from portfolio.tests.test_views_public import create_test_profile

VALID = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'subject': 'Project collaboration',
    'message': 'I would like to discuss a potential project with you.',
}


def _fake_recaptcha(success=True, score=0.9, action='contact'):
    """Patch target for urllib.request.urlopen returning a reCAPTCHA verdict."""
    import json

    payload = {'success': success, 'score': score, 'action': action}

    class _Resp:
        def read(self):
            return json.dumps(payload).encode()

    return mock.Mock(return_value=_Resp())


class ContactFormValidationTests(TestCase):
    """Form-level filters (Fix 4 + Fix 5)."""

    def test_subject_spam_rejected(self):
        data = {**VALID, 'subject': 'URGENT! WITHDRAW 1.3426 BTC NOW'}
        form = SecureContactFormWithHoneypot(data)
        self.assertFalse(form.is_valid())
        self.assertIn('subject', form.errors)

    def test_btc_keyword_in_subject_rejected(self):
        # Regression: 'btc' was missing from the keyword list before.
        data = {**VALID, 'subject': 'your 1.3426 btc is ready to withdraw'}
        self.assertFalse(SecureContactFormWithHoneypot(data).is_valid())

    def test_message_spam_rejected(self):
        data = {**VALID, 'message': 'Claim your free bitcoin wallet right now!!!'}
        self.assertFalse(SecureContactFormWithHoneypot(data).is_valid())

    def test_too_fast_submission_rejected(self):
        data = {**VALID, 'form_loaded_at': str(time.time())}  # elapsed ~0s
        self.assertFalse(SecureContactFormWithHoneypot(data).is_valid())

    def test_normal_submission_is_valid(self):
        data = {**VALID, 'form_loaded_at': str(time.time() - 30)}
        form = SecureContactFormWithHoneypot(data)
        self.assertTrue(form.is_valid(), form.errors)


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    CACHES={'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-contact-spam',
    }},
)
class ContactViewSecurityTests(TestCase):
    """View-level defenses (Fix 1 + Fix 2 + Fix 3)."""

    def setUp(self):
        cache.clear()
        self.url = reverse('portfolio:home')
        # Raw-SQL helper: Profile has legacy NOT NULL columns that .create() trips on.
        create_test_profile(email='owner@example.com')

    def _payload(self, **over):
        data = {**VALID, 'form_loaded_at': str(time.time() - 30), 'honeypot': ''}
        data.update(over)
        return data

    @mock.patch.dict('os.environ', {'RECAPTCHA_SECRET_KEY': 'test-secret'})
    def test_recaptcha_fail_closed_without_token(self):
        # Bot posts directly without a reCAPTCHA token -> must be rejected.
        resp = self.client.post(self.url, self._payload())
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Contact.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    @mock.patch.dict('os.environ', {'RECAPTCHA_SECRET_KEY': 'test-secret'})
    def test_recaptcha_low_score_rejected(self):
        with mock.patch('urllib.request.urlopen', _fake_recaptcha(score=0.1)):
            resp = self.client.post(self.url, self._payload(**{'g-recaptcha-response': 'tok'}))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Contact.objects.count(), 0)

    @mock.patch.dict('os.environ', {'RECAPTCHA_SECRET_KEY': 'test-secret'})
    def test_recaptcha_valid_token_accepted(self):
        with mock.patch('urllib.request.urlopen', _fake_recaptcha(score=0.9)):
            resp = self.client.post(self.url, self._payload(**{'g-recaptcha-response': 'tok'}))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Contact.objects.count(), 1)

    @mock.patch.dict('os.environ', {'RECAPTCHA_SECRET_KEY': ''})
    def test_no_confirmation_email_to_sender(self):
        # With reCAPTCHA disabled, a valid submission still must NOT email the
        # sender-supplied address (the relay vector). Only the owner is notified.
        resp = self.client.post(self.url, self._payload())
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Contact.objects.count(), 1)
        recipients = [addr for m in mail.outbox for addr in m.to]
        self.assertNotIn(VALID['email'], recipients)

    @mock.patch.dict('os.environ', {'RECAPTCHA_SECRET_KEY': '', 'CONTACT_MAX_PER_HOUR': '3'})
    def test_rate_limit_blocks_flood(self):
        for _ in range(3):
            self.client.post(self.url, self._payload())
        self.assertEqual(Contact.objects.count(), 3)
        # 4th submission within the window is blocked before any DB write.
        self.client.post(self.url, self._payload())
        self.assertEqual(Contact.objects.count(), 3)
