# Umami Analytics Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Load a deployer-configured Umami tracking script on public pages (never for logged-in users) and derive the CSP analytics origin from that configuration instead of a hardcoded domain.

**Architecture:** Two fields on the `SiteConfiguration` singleton (dashboard-editable, same pattern as the newsletter CTA), a conditional `<script>` in `base.html`, and a cached helper in the security middleware that injects the configured origin into the CSP. Empty config = no script, no analytics origin in CSP.

**Tech Stack:** Django 5.2, pytest (`--ds` per environment note below), Django cache (locmem in tests).

**Spec:** `docs/superpowers/specs/2026-08-08-umami-analytics-design.md` (Phase 1 section) · **Issue:** #117

## Global Constraints

- **Prerequisite:** PR #118 must be MERGED first (`gh pr view 118 --json state`). Then: `git fetch origin && git rebase origin/main` on this branch before Task 1. Reason: this plan anchors on the newsletter dashboard section, reuses the fixed `i18n_compiler`, and must take the migration number after `0039`.
- **Sequencing:** never execute this plan in parallel with the UUID-filenames plan (both generate migrations; whichever runs first takes the next number).
- **No hardcoded domains:** `analytics.henfrydls.com` must not survive anywhere in code. Empty config renders no script and adds no origin to CSP.
- **The script never renders for authenticated users** (`user.is_authenticated`).
- Test command: `POSTGRES_HOST=127.0.0.1 POSTGRES_PORT=54329 ~/.venvs/portafolio-manager/bin/python -m pytest -p no:cacheprovider <args>` (embedded Postgres; start command in the memory note if it's down). Same env vars for `manage.py`.
- Commits: conventional style; never mention AI assistance or Claude. Never `git add -A` (untracked personal files exist). Never merge the PR.
- All code, comments and repo artifacts in English.

---

### Task 1: `SiteConfiguration` analytics fields + migration

**Files:**
- Modify: `portfolio/models.py` (insert after `newsletter_button_text`, before `updated_at`)
- Create: `portfolio/migrations/00NN_*.py` (generated — number assigned by makemigrations)
- Test: `portfolio/tests/test_models.py` (append at end)

**Interfaces:**
- Produces: `SiteConfiguration.umami_script_url`, `.umami_website_id` — `str`, default `''`, `blank=True`. Read via `site_config` template variable and `SiteConfiguration.get_solo()`.

- [ ] **Step 1: Write the failing test** — append to `portfolio/tests/test_models.py`:

```python
class SiteConfigurationUmamiFieldsTest(TestCase):
    """Umami analytics configuration fields (issue #117)."""

    def test_umami_fields_default_empty(self):
        config = SiteConfiguration.get_solo()
        self.assertEqual(config.umami_script_url, '')
        self.assertEqual(config.umami_website_id, '')

    def test_umami_fields_persist(self):
        config = SiteConfiguration.get_solo()
        config.umami_script_url = 'https://stats.example.com/script.js'
        config.umami_website_id = 'abc123-def456'
        config.save()
        config.refresh_from_db()
        self.assertEqual(config.umami_script_url, 'https://stats.example.com/script.js')
        self.assertEqual(config.umami_website_id, 'abc123-def456')
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest portfolio/tests/test_models.py -k Umami -v` (with the env prefix)
Expected: FAIL with `AttributeError: 'SiteConfiguration' object has no attribute 'umami_script_url'`

- [ ] **Step 3: Add the fields** — in `portfolio/models.py`, after `newsletter_button_text` and before `updated_at`:

```python
    umami_script_url = models.URLField(
        blank=True,
        default='',
        verbose_name="Umami script URL",
        help_text="Full URL of the Umami tracking script, e.g. https://stats.example.com/script.js. Leave empty to disable analytics."
    )
    umami_website_id = models.CharField(
        max_length=64,
        blank=True,
        default='',
        verbose_name="Umami website ID",
        help_text="Website ID from your Umami dashboard."
    )
```

- [ ] **Step 4: Generate the migration**

Run: `python manage.py makemigrations portfolio` (with the env prefix)
Expected: one migration adding exactly the two fields.

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest portfolio/tests/test_models.py -k Umami -v`
Expected: 2 PASSED

- [ ] **Step 6: Commit**

```bash
git add portfolio/models.py portfolio/migrations/ portfolio/tests/test_models.py
git commit -m "feat: add Umami analytics fields to SiteConfiguration (#117)"
```

---

### Task 2: Dashboard form and template fields

**Files:**
- Modify: `portfolio/forms/config.py` (`SiteConfigurationForm.Meta`)
- Modify: `templates/portfolio/admin/site_configuration.html` (after the Newsletter dashed box added by PR #118 — the box containing `form.newsletter_button_text`)
- Test: `portfolio/tests/test_forms.py` (append at end)

**Interfaces:**
- Consumes: the two fields from Task 1.
- Produces: `SiteConfigurationForm` accepts and persists `umami_script_url`, `umami_website_id`; both optional.

- [ ] **Step 1: Write the failing tests** — append to `portfolio/tests/test_forms.py` (the newsletter test class from PR #118 already imports `SiteConfigurationForm` and `SiteConfiguration`):

```python
class SiteConfigurationFormUmamiTest(TestCase):
    """Umami fields on the site configuration form (issue #117)."""

    BASE_DATA = {
        'default_language': 'en',
        'translation_provider': 'libretranslate',
        'translation_timeout': 60,
    }

    def test_form_saves_umami_fields(self):
        config = SiteConfiguration.get_solo()
        data = dict(self.BASE_DATA)
        data.update({
            'umami_script_url': 'https://stats.example.com/script.js',
            'umami_website_id': 'abc123-def456',
        })
        form = SiteConfigurationForm(data=data, instance=config)
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save()
        self.assertEqual(saved.umami_script_url, 'https://stats.example.com/script.js')
        self.assertEqual(saved.umami_website_id, 'abc123-def456')

    def test_umami_fields_are_optional(self):
        config = SiteConfiguration.get_solo()
        form = SiteConfigurationForm(data=dict(self.BASE_DATA), instance=config)
        self.assertTrue(form.is_valid(), form.errors)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest portfolio/tests/test_forms.py -k Umami -v`
Expected: FAIL — `umami_script_url` not in `form.fields`, first test's assertion fails.

- [ ] **Step 3: Add fields to the form** — in `portfolio/forms/config.py`, append to `Meta.fields` after `'newsletter_button_text'`:

```python
            'umami_script_url',
            'umami_website_id',
```

Add to the `widgets` dict:

```python
            'umami_script_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://stats.example.com/script.js'}),
            'umami_website_id': forms.TextInput(attrs={'class': 'form-control'}),
```

- [ ] **Step 4: Add the dashboard section** — in `templates/portfolio/admin/site_configuration.html`, insert after the closing `</div>` of the Newsletter dashed box (the one containing `form.newsletter_button_text`), as a sibling:

```html
                <div style="display: grid; gap: 16px; padding: 16px; background: #f8f9fa; border: 1px dashed #dce3ed; border-radius: 8px;">
                    <label class="form-label-custom">{% trans "Analytics" %}</label>
                    <div>
                        <label for="{{ form.umami_script_url.id_for_label }}" class="form-label-custom">
                            {{ form.umami_script_url.label }}
                        </label>
                        {{ form.umami_script_url }}
                        {% if form.umami_script_url.errors %}
                        <p class="form-error">{{ form.umami_script_url.errors|first }}</p>
                        {% else %}
                        <p class="form-help">{% trans "Full URL of the Umami tracking script. Leave empty to disable analytics." %}</p>
                        {% endif %}
                    </div>
                    <div>
                        <label for="{{ form.umami_website_id.id_for_label }}" class="form-label-custom">
                            {{ form.umami_website_id.label }}
                        </label>
                        {{ form.umami_website_id }}
                        {% if form.umami_website_id.errors %}
                        <p class="form-error">{{ form.umami_website_id.errors|first }}</p>
                        {% else %}
                        <p class="form-help">{% trans "Website ID from your Umami dashboard." %}</p>
                        {% endif %}
                    </div>
                </div>
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest portfolio/tests/test_forms.py -k Umami -v`
Expected: 2 PASSED

- [ ] **Step 6: Commit**

```bash
git add portfolio/forms/config.py templates/portfolio/admin/site_configuration.html portfolio/tests/test_forms.py
git commit -m "feat: Umami analytics settings editable from the dashboard (#117)"
```

---

### Task 3: Conditional tracking script in `base.html`

**Files:**
- Modify: `templates/base.html` (immediately before `</head>`, ~line 382)
- Test: `portfolio/tests/test_views_public.py` (append at end)

**Interfaces:**
- Consumes: `site_config.umami_script_url` / `.umami_website_id` (Task 1) via the context processor.

- [ ] **Step 1: Write the failing tests** — append to `portfolio/tests/test_views_public.py` (reuse `create_test_profile`, `User`, `Client`; `SiteConfiguration` is imported since PR #118):

```python
class UmamiScriptTest(TestCase):
    """Conditional Umami tracking script (issue #117)."""

    def setUp(self):
        self.client = Client()
        self.profile = create_test_profile()
        translation.activate('en')
        self.admin = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='testpass123'
        )

    def _configure(self):
        config = SiteConfiguration.get_solo()
        config.umami_script_url = 'https://stats.example.com/script.js'
        config.umami_website_id = 'abc123-def456'
        config.save()

    def test_no_script_without_configuration(self):
        response = self.client.get(reverse('portfolio:home'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'data-website-id')

    def test_script_renders_for_anonymous_visitor(self):
        self._configure()
        response = self.client.get(reverse('portfolio:home'))
        self.assertContains(response, 'https://stats.example.com/script.js')
        self.assertContains(response, 'data-website-id="abc123-def456"')

    def test_no_script_for_authenticated_user(self):
        self._configure()
        self.client.force_login(self.admin)
        response = self.client.get(reverse('portfolio:home'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'data-website-id')
```

Note: if `reverse('portfolio:home')` is not the home route name, check `portfolio/urls.py` for the `''` path's name and use that; the existing `HomeViewTest` class shows the working pattern.

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest portfolio/tests/test_views_public.py -k UmamiScript -v`
Expected: first test PASSES (nothing renders today), the other two FAIL.

- [ ] **Step 3: Add the script tag** — in `templates/base.html`, immediately before `</head>`:

```html
    <!-- Umami analytics (only when configured, never for logged-in users) -->
    {% if site_config.umami_script_url and site_config.umami_website_id and not user.is_authenticated %}
    <script defer src="{{ site_config.umami_script_url }}" data-website-id="{{ site_config.umami_website_id }}"></script>
    {% endif %}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest portfolio/tests/test_views_public.py -k UmamiScript -v`
Expected: 3 PASSED

- [ ] **Step 5: Commit**

```bash
git add templates/base.html portfolio/tests/test_views_public.py
git commit -m "feat: load the configured Umami tracking script on public pages (#117)"
```

---

### Task 4: CSP analytics origin derived from configuration

**Files:**
- Modify: `portfolio/middleware/security.py` (`SecurityHeadersMiddleware.process_response`, lines 20–58; add a module-level helper)
- Test: `portfolio/tests/test_security_headers.py` (new file)

**Interfaces:**
- Produces: `get_analytics_origin() -> str` in `portfolio/middleware/security.py` — cached (Django cache key `umami_analytics_origin`, TTL 300s), returns `'https://host'` or `''`.

- [ ] **Step 1: Write the failing tests** — create `portfolio/tests/test_security_headers.py`:

```python
"""Tests for the CSP analytics origin (issue #117)."""
from django.core.cache import cache
from django.http import HttpResponse
from django.test import TestCase, RequestFactory

from portfolio.middleware.security import SecurityHeadersMiddleware, get_analytics_origin
from portfolio.models import SiteConfiguration


class CspAnalyticsOriginTest(TestCase):

    def setUp(self):
        cache.delete('umami_analytics_origin')
        self.factory = RequestFactory()
        self.middleware = SecurityHeadersMiddleware(lambda request: HttpResponse())

    def _csp(self):
        request = self.factory.get('/')
        response = self.middleware.process_response(request, HttpResponse())
        return response['Content-Security-Policy']

    def test_no_analytics_origin_without_configuration(self):
        csp = self._csp()
        self.assertNotIn('analytics.henfrydls.com', csp)
        self.assertNotIn('stats.example.com', csp)

    def test_configured_origin_in_script_and_connect_src(self):
        config = SiteConfiguration.get_solo()
        config.umami_script_url = 'https://stats.example.com/script.js'
        config.save()
        cache.delete('umami_analytics_origin')
        csp = self._csp()
        directives = {d.strip().split(' ')[0]: d.strip() for d in csp.split(';') if d.strip()}
        self.assertIn('https://stats.example.com', directives['script-src'])
        self.assertIn('https://stats.example.com', directives['connect-src'])
        self.assertNotIn('analytics.henfrydls.com', csp)

    def test_helper_returns_origin_only(self):
        config = SiteConfiguration.get_solo()
        config.umami_script_url = 'https://stats.example.com/script.js'
        config.save()
        cache.delete('umami_analytics_origin')
        self.assertEqual(get_analytics_origin(), 'https://stats.example.com')
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest portfolio/tests/test_security_headers.py -v`
Expected: FAIL — `get_analytics_origin` does not exist; the hardcoded domain is present.

- [ ] **Step 3: Implement** — in `portfolio/middleware/security.py`, add after the `logger` line:

```python
def get_analytics_origin():
    """Origin of the configured Umami instance, cached for 5 minutes; '' when unconfigured."""
    value = cache.get('umami_analytics_origin')
    if value is not None:
        return value
    from urllib.parse import urlparse
    try:
        from portfolio.models import SiteConfiguration
        url = SiteConfiguration.get_solo().umami_script_url
    except Exception:
        url = ''
    parsed = urlparse(url) if url else None
    value = f'{parsed.scheme}://{parsed.netloc}' if parsed and parsed.scheme and parsed.netloc else ''
    cache.set('umami_analytics_origin', value, 300)
    return value
```

Replace the `csp_policy` block (current lines 22–41) with:

```python
        analytics_origin = get_analytics_origin()
        analytics_src = f'{analytics_origin} ' if analytics_origin else ''
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
            "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com "
            "https://fonts.googleapis.com https://unpkg.com "
            "https://www.google.com/recaptcha/ https://www.gstatic.com/recaptcha/ "
            f"{analytics_src}"
            "; "
            "style-src 'self' 'unsafe-inline' "
            "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com "
            "https://fonts.googleapis.com https://unpkg.com; "
            "font-src 'self' https://fonts.gstatic.com "
            "https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "frame-src https://www.google.com/recaptcha/; "
            f"connect-src 'self' https://cdn.jsdelivr.net {analytics_src}; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
```

Note the trailing-space handling: `analytics_src` already carries its trailing space when non-empty, so the literal `"; "` after it closes `script-src` cleanly in both cases.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest portfolio/tests/test_security_headers.py -v`
Expected: 3 PASSED

- [ ] **Step 5: Commit**

```bash
git add portfolio/middleware/security.py portfolio/tests/test_security_headers.py
git commit -m "feat: derive the CSP analytics origin from site configuration (#117)"
```

---

### Task 5: Spanish translations for the new dashboard strings

**Files:**
- Modify: `locale/es/LC_MESSAGES/django.po` (and regenerate `django.mo`)
- Test: none new (dashboard strings; rendering is already covered). Verify compilation only.

- [ ] **Step 1: Add the entries** — append to `locale/es/LC_MESSAGES/django.po` (grep first to avoid duplicates):

```po
msgid "Analytics"
msgstr "Analítica"

msgid "Full URL of the Umami tracking script. Leave empty to disable analytics."
msgstr "URL completa del script de Umami. Vacío desactiva la analítica."

msgid "Website ID from your Umami dashboard."
msgstr "ID del sitio en tu panel de Umami."
```

- [ ] **Step 2: Compile the catalog**

Run: `python manage.py compilemessages -l es`; if gettext is missing, use the project fallback:
`python -c "from portfolio.i18n_compiler import compile_po_to_mo; compile_po_to_mo('locale/es/LC_MESSAGES/django.po', 'locale/es/LC_MESSAGES/django.mo')"`

- [ ] **Step 3: Spot-check the catalog didn't regress** — run the existing Spanish rendering test from PR #118:

Run: `python -m pytest portfolio/tests/test_views_public.py -k spanish -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add locale/es/LC_MESSAGES/django.po locale/es/LC_MESSAGES/django.mo
git commit -m "feat: Spanish translations for the analytics settings (#117)"
```

---

### Task 6: Full suite, push, PR

- [ ] **Step 1: Run the entire test suite**

Run: `python -m pytest portfolio/tests/ -q`
Expected: everything green.

- [ ] **Step 2: Push and open the PR** (do NOT merge):

```bash
git push -u origin feat/umami-analytics
gh pr create --title "feat: Umami analytics integration — phase 1 (tracking script + CSP)" \
  --body "Phase 1 of #117.

- Two optional SiteConfiguration fields (script URL + website ID), dashboard-editable.
- base.html loads the tracking script only when configured and never for authenticated users.
- CSP script-src/connect-src analytics origin is derived from the configured URL — the hardcoded domain is gone.
- With no configuration, pages render no script and the CSP carries no analytics origin.
- Phases 2 (dashboard stats via Umami API) and 3 (events) follow in separate PRs.
- Design spec: docs/superpowers/specs/2026-08-08-umami-analytics-design.md"
```

- [ ] **Step 3: Report the PR URL and stop.** Instance provisioning (creating the website entry in the deployer's Umami and pasting the values in the dashboard) is deployment configuration, not code.
