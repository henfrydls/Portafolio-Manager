# Configurable Subscribe CTA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the end-of-post contact CTA with a configurable newsletter subscribe block when (and only when) a `newsletter_url` is configured, with generic translatable default copy and optional custom copy.

**Architecture:** Four optional fields on the `SiteConfiguration` singleton (already exposed to every template via the `site_config` context processor), a dashboard form to edit them, and a template include that `blog_detail.html` renders instead of the existing contact CTA when the URL is set. No new views, no new CSS, no JS.

**Tech Stack:** Django 4.x, django-parler (untouched here), pytest (`DJANGO_SETTINGS_MODULE=config.settings.test` from `pyproject.toml`), Django template i18n (`{% trans %}`).

**Spec:** `docs/superpowers/specs/2026-08-08-newsletter-cta-design.md` · **Issue:** #116

## Global Constraints

- **Backward compatibility:** with `newsletter_url` empty, post pages render the existing contact CTA exactly as today.
- **Generic default copy, verbatim:** title `Newsletter`, description `Get notified when new posts are published.`, button `Subscribe`.
- **Button attributes, verbatim:** `data-umami-event="newsletter-subscribe"`, `target="_blank" rel="noopener"`.
- **No new CSS.** Reuse classes `post-contact-cta`, `cta-content`, `cta-title`, `cta-text`, `cta-button`.
- **Commits:** conventional style (`feat:`, `test:`, `docs:`). Never mention AI assistance or Claude in commits or PRs. Never merge the PR.
- **Tests:** run with `python -m pytest` from the repo root (venv already configured). No network access in tests.
- All code, comments and repo artifacts in English.
- Work happens on branch `feat/newsletter-cta` (already exists, holds the spec).

---

### Task 1: `SiteConfiguration` newsletter fields + migration

**Files:**
- Modify: `portfolio/models.py` (insert after `translation_timeout`, ~line 60, before `updated_at`)
- Create: `portfolio/migrations/0039_*.py` (generated)
- Test: `portfolio/tests/test_models.py` (append at end; `SiteConfiguration` is already imported)

**Interfaces:**
- Produces: `SiteConfiguration.newsletter_url`, `.newsletter_title`, `.newsletter_description`, `.newsletter_button_text` — all `str`, default `''`, `blank=True`. Later tasks read them via `SiteConfiguration.get_solo()` / the `site_config` template variable.

- [ ] **Step 1: Write the failing test** — append to `portfolio/tests/test_models.py`:

```python
class SiteConfigurationNewsletterFieldsTest(TestCase):
    """Newsletter CTA configuration fields (issue #116)."""

    def test_newsletter_fields_default_empty(self):
        config = SiteConfiguration.get_solo()
        self.assertEqual(config.newsletter_url, '')
        self.assertEqual(config.newsletter_title, '')
        self.assertEqual(config.newsletter_description, '')
        self.assertEqual(config.newsletter_button_text, '')

    def test_newsletter_fields_persist(self):
        config = SiteConfiguration.get_solo()
        config.newsletter_url = 'https://www.linkedin.com/newsletters/example-123/'
        config.newsletter_title = 'My Newsletter'
        config.newsletter_description = 'One issue a month.'
        config.newsletter_button_text = 'Subscribe on LinkedIn'
        config.save()
        config.refresh_from_db()
        self.assertEqual(config.newsletter_url, 'https://www.linkedin.com/newsletters/example-123/')
        self.assertEqual(config.newsletter_title, 'My Newsletter')
        self.assertEqual(config.newsletter_description, 'One issue a month.')
        self.assertEqual(config.newsletter_button_text, 'Subscribe on LinkedIn')
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest portfolio/tests/test_models.py -k Newsletter -v`
Expected: FAIL with `AttributeError: 'SiteConfiguration' object has no attribute 'newsletter_url'`

- [ ] **Step 3: Add the fields** — in `portfolio/models.py`, immediately after the `translation_timeout` field and before `updated_at`:

```python
    newsletter_url = models.URLField(
        blank=True,
        default='',
        verbose_name="Newsletter URL",
        help_text="Destination of the end-of-post subscribe button. Leave empty to keep the contact CTA."
    )
    newsletter_title = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name="Newsletter title",
        help_text="Optional. Replaces the generic 'Newsletter' heading."
    )
    newsletter_description = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name="Newsletter description",
        help_text="Optional. Replaces the generic description."
    )
    newsletter_button_text = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name="Newsletter button text",
        help_text="Optional. Replaces the generic 'Subscribe' label."
    )
```

- [ ] **Step 4: Generate the migration**

Run: `python manage.py makemigrations portfolio`
Expected: creates `portfolio/migrations/0039_siteconfiguration_newsletter_button_text_and_more.py` (name may vary; must add exactly the four fields).

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest portfolio/tests/test_models.py -k Newsletter -v`
Expected: 2 PASSED

- [ ] **Step 6: Commit**

```bash
git add portfolio/models.py portfolio/migrations/ portfolio/tests/test_models.py
git commit -m "feat: add newsletter CTA fields to SiteConfiguration (#116)"
```

---

### Task 2: Dashboard form and template fields

**Files:**
- Modify: `portfolio/forms/config.py` (`SiteConfigurationForm.Meta`)
- Modify: `templates/portfolio/admin/site_configuration.html` (after the dashed translation box, which closes after the `translation_timeout` block ~line 119)
- Test: `portfolio/tests/test_forms.py` (append at end)

**Interfaces:**
- Consumes: the four `SiteConfiguration` fields from Task 1.
- Produces: `SiteConfigurationForm` accepts and persists `newsletter_url`, `newsletter_title`, `newsletter_description`, `newsletter_button_text`; all optional.

- [ ] **Step 1: Write the failing tests** — append to `portfolio/tests/test_forms.py` (add the imports below if missing):

```python
from portfolio.forms.config import SiteConfigurationForm
from portfolio.models import SiteConfiguration


class SiteConfigurationFormNewsletterTest(TestCase):
    """Newsletter fields on the site configuration form (issue #116)."""

    BASE_DATA = {
        'default_language': 'en',
        'translation_provider': 'libretranslate',
        'translation_timeout': 60,
    }

    def test_form_saves_newsletter_fields(self):
        config = SiteConfiguration.get_solo()
        data = dict(self.BASE_DATA)
        data.update({
            'newsletter_url': 'https://example.com/newsletter/',
            'newsletter_title': 'My Newsletter',
            'newsletter_description': 'One issue a month.',
            'newsletter_button_text': 'Subscribe now',
        })
        form = SiteConfigurationForm(data=data, instance=config)
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save()
        self.assertEqual(saved.newsletter_url, 'https://example.com/newsletter/')
        self.assertEqual(saved.newsletter_title, 'My Newsletter')
        self.assertEqual(saved.newsletter_description, 'One issue a month.')
        self.assertEqual(saved.newsletter_button_text, 'Subscribe now')

    def test_newsletter_fields_are_optional(self):
        config = SiteConfiguration.get_solo()
        form = SiteConfigurationForm(data=dict(self.BASE_DATA), instance=config)
        self.assertTrue(form.is_valid(), form.errors)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest portfolio/tests/test_forms.py -k Newsletter -v`
Expected: FAIL — `newsletter_url` not in `form.fields`, so `save()` leaves the values empty (first test asserts and fails).

- [ ] **Step 3: Add fields to the form** — in `portfolio/forms/config.py`, extend `Meta.fields` and `Meta.widgets`:

```python
        fields = [
            'default_language',
            'auto_translate_enabled',
            'translation_provider',
            'translation_api_url',
            'translation_api_key',
            'translation_timeout',
            'newsletter_url',
            'newsletter_title',
            'newsletter_description',
            'newsletter_button_text',
        ]
```

Add to the `widgets` dict:

```python
            'newsletter_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'newsletter_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Newsletter'}),
            'newsletter_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Get notified when new posts are published.'}),
            'newsletter_button_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subscribe'}),
```

- [ ] **Step 4: Add the dashboard section** — in `templates/portfolio/admin/site_configuration.html`, insert after the closing `</div>` of the dashed translation box (the box that contains `form.translation_timeout`), as a sibling inside the `display: grid; gap: 24px` container:

```html
                <div style="display: grid; gap: 16px; padding: 16px; background: #f8f9fa; border: 1px dashed #dce3ed; border-radius: 8px;">
                    <label class="form-label-custom">{% trans "Newsletter" %}</label>
                    <div>
                        <label for="{{ form.newsletter_url.id_for_label }}" class="form-label-custom">
                            {{ form.newsletter_url.label }}
                        </label>
                        {{ form.newsletter_url }}
                        {% if form.newsletter_url.errors %}
                        <p class="form-error">{{ form.newsletter_url.errors|first }}</p>
                        {% else %}
                        <p class="form-help">{% trans "Destination of the end-of-post subscribe button. Leave empty to keep the contact CTA." %}</p>
                        {% endif %}
                    </div>
                    <div>
                        <label for="{{ form.newsletter_title.id_for_label }}" class="form-label-custom">
                            {{ form.newsletter_title.label }}
                        </label>
                        {{ form.newsletter_title }}
                        {% if form.newsletter_title.errors %}
                        <p class="form-error">{{ form.newsletter_title.errors|first }}</p>
                        {% else %}
                        <p class="form-help">{% trans "Optional. Replaces the generic 'Newsletter' heading." %}</p>
                        {% endif %}
                    </div>
                    <div>
                        <label for="{{ form.newsletter_description.id_for_label }}" class="form-label-custom">
                            {{ form.newsletter_description.label }}
                        </label>
                        {{ form.newsletter_description }}
                        {% if form.newsletter_description.errors %}
                        <p class="form-error">{{ form.newsletter_description.errors|first }}</p>
                        {% else %}
                        <p class="form-help">{% trans "Optional. Replaces the generic description." %}</p>
                        {% endif %}
                    </div>
                    <div>
                        <label for="{{ form.newsletter_button_text.id_for_label }}" class="form-label-custom">
                            {{ form.newsletter_button_text.label }}
                        </label>
                        {{ form.newsletter_button_text }}
                        {% if form.newsletter_button_text.errors %}
                        <p class="form-error">{{ form.newsletter_button_text.errors|first }}</p>
                        {% else %}
                        <p class="form-help">{% trans "Optional. Replaces the generic 'Subscribe' label." %}</p>
                        {% endif %}
                    </div>
                </div>
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest portfolio/tests/test_forms.py -k Newsletter -v`
Expected: 2 PASSED

- [ ] **Step 6: Commit**

```bash
git add portfolio/forms/config.py templates/portfolio/admin/site_configuration.html portfolio/tests/test_forms.py
git commit -m "feat: newsletter CTA settings editable from the dashboard (#116)"
```

---

### Task 3: Subscribe block include + conditional in `blog_detail.html`

**Files:**
- Create: `templates/portfolio/includes/subscribe_cta.html`
- Modify: `templates/portfolio/blog_detail.html` (the `post-contact-cta` block, lines 213–222)
- Test: `portfolio/tests/test_views_public.py` (append at end)

**Interfaces:**
- Consumes: `site_config.newsletter_url` / `_title` / `_description` / `_button_text` (Task 1) via the existing `site_config` context-processor variable.
- Produces: the rendered block later referenced by the Umami integration (event name `newsletter-subscribe`).

- [ ] **Step 1: Write the failing tests** — append to `portfolio/tests/test_views_public.py` (mirror the imports/setup style of the existing `BlogDetailView` test class; `SiteConfiguration` must be added to the `portfolio.models` import line):

```python
class BlogDetailSubscribeCtaTest(TestCase):
    """End-of-post subscribe CTA (issue #116)."""

    def setUp(self):
        self.client = Client()
        self.profile = create_test_profile()
        translation.activate('en')
        User.objects.create_superuser(
            username='admin', email='admin@example.com', password='testpass123'
        )
        self.category = Category.objects.create(slug='tech')
        self.category.set_current_language('en')
        self.category.name = "Technology"
        self.category.description = "Tech posts"
        self.category.save()
        self.post = BlogPost()
        self.post.set_current_language('en')
        self.post.title = "Test Post"
        self.post.content = "Test content"
        self.post.excerpt = "Test excerpt"
        self.post.category = self.category
        self.post.status = 'published'
        self.post.publish_date = timezone.now()
        self.post.save()
        self.url = reverse('portfolio:post-detail', kwargs={'slug': self.post.slug})

    def test_contact_cta_renders_without_newsletter_url(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Start a conversation')
        self.assertNotContains(response, 'newsletter-subscribe')

    def test_subscribe_block_with_generic_copy(self):
        config = SiteConfiguration.get_solo()
        config.newsletter_url = 'https://example.com/nl/'
        config.save()
        response = self.client.get(self.url)
        self.assertContains(response, 'https://example.com/nl/')
        self.assertContains(response, 'data-umami-event="newsletter-subscribe"')
        self.assertContains(response, 'Get notified when new posts are published.')
        self.assertContains(response, 'Subscribe')
        self.assertNotContains(response, 'Start a conversation')

    def test_subscribe_block_with_custom_copy(self):
        config = SiteConfiguration.get_solo()
        config.newsletter_url = 'https://example.com/nl/'
        config.newsletter_title = 'Proof of Concept'
        config.newsletter_description = 'Ideas tested inside a real company.'
        config.newsletter_button_text = 'Subscribe on LinkedIn'
        config.save()
        response = self.client.get(self.url)
        self.assertContains(response, 'Proof of Concept')
        self.assertContains(response, 'Ideas tested inside a real company.')
        self.assertContains(response, 'Subscribe on LinkedIn')
        self.assertNotContains(response, 'Get notified when new posts are published.')
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest portfolio/tests/test_views_public.py -k SubscribeCta -v`
Expected: first test PASSES (current behavior), the other two FAIL (`newsletter-subscribe` not in response).

- [ ] **Step 3: Create the include** — `templates/portfolio/includes/subscribe_cta.html`:

```html
{% load i18n %}
{% if site_config.newsletter_url %}
<!-- Newsletter Subscribe CTA (replaces the contact CTA when configured) -->
<div class="post-contact-cta">
    <div class="cta-content">
        <h4 class="cta-title">{% if site_config.newsletter_title %}{{ site_config.newsletter_title }}{% else %}{% trans "Newsletter" %}{% endif %}</h4>
        <p class="cta-text">{% if site_config.newsletter_description %}{{ site_config.newsletter_description }}{% else %}{% trans "Get notified when new posts are published." %}{% endif %}</p>
        <a href="{{ site_config.newsletter_url }}" target="_blank" rel="noopener" class="cta-button" data-umami-event="newsletter-subscribe">
            {% if site_config.newsletter_button_text %}{{ site_config.newsletter_button_text }}{% else %}{% trans "Subscribe" %}{% endif %}
        </a>
    </div>
</div>
{% endif %}
```

- [ ] **Step 4: Make `blog_detail.html` conditional** — replace lines 213–222 (the `<!-- Subtle Contact CTA -->` block) with:

```html
                    {% if site_config.newsletter_url %}
                    {% include 'portfolio/includes/subscribe_cta.html' %}
                    {% else %}
                    <!-- Subtle Contact CTA -->
                    <div class="post-contact-cta">
                        <div class="cta-content">
                            <h4 class="cta-title">{% trans "Enjoyed this post?" %}</h4>
                            <p class="cta-text">{% trans "Let's discuss your next project or share thoughts on this topic." %}</p>
                            <a href="javascript:void(0)" onclick="openContactModal()" class="cta-button">
                                {% trans "Start a conversation" %}
                            </a>
                        </div>
                    </div>
                    {% endif %}
```

(The `{% else %}` branch is the existing block verbatim — do not reword it.)

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest portfolio/tests/test_views_public.py -k SubscribeCta -v`
Expected: 3 PASSED

- [ ] **Step 6: Commit**

```bash
git add templates/portfolio/includes/subscribe_cta.html templates/portfolio/blog_detail.html portfolio/tests/test_views_public.py
git commit -m "feat: configurable subscribe CTA at the end of blog posts (#116)"
```

---

### Task 4: Spanish translations for the new strings

**Files:**
- Modify: `locale/es/LC_MESSAGES/django.po` (and regenerate `django.mo`)
- Test: `portfolio/tests/test_views_public.py` (append to `BlogDetailSubscribeCtaTest`)

**Interfaces:**
- Consumes: the `{% trans %}` msgids introduced in Tasks 2–3.

- [ ] **Step 1: Write the failing test** — append inside `BlogDetailSubscribeCtaTest` (add `from django.template.loader import render_to_string` and `from django.utils.translation import override` to the file imports):

```python
    def test_subscribe_block_generic_copy_in_spanish(self):
        config = SiteConfiguration.get_solo()
        config.newsletter_url = 'https://example.com/nl/'
        config.save()
        with override('es'):
            html = render_to_string(
                'portfolio/includes/subscribe_cta.html',
                {'site_config': config},
            )
        self.assertIn('Suscribirse', html)
        self.assertIn('Entérate cuando se publiquen nuevos posts.', html)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest portfolio/tests/test_views_public.py -k spanish -v`
Expected: FAIL — English fallback rendered (`Subscribe`), Spanish strings missing.

- [ ] **Step 3: Add the entries** — append to `locale/es/LC_MESSAGES/django.po` (respect the file's existing entry format):

```po
msgid "Newsletter"
msgstr "Newsletter"

msgid "Get notified when new posts are published."
msgstr "Entérate cuando se publiquen nuevos posts."

msgid "Subscribe"
msgstr "Suscribirse"

msgid "Destination of the end-of-post subscribe button. Leave empty to keep the contact CTA."
msgstr "Destino del botón de suscripción al final de cada post. Vacío mantiene el CTA de contacto."

msgid "Optional. Replaces the generic 'Newsletter' heading."
msgstr "Opcional. Reemplaza el título genérico 'Newsletter'."

msgid "Optional. Replaces the generic description."
msgstr "Opcional. Reemplaza la descripción genérica."

msgid "Optional. Replaces the generic 'Subscribe' label."
msgstr "Opcional. Reemplaza el texto genérico del botón."
```

Before adding, check each msgid doesn't already exist in the file (`grep -n 'msgid "Newsletter"' locale/es/LC_MESSAGES/django.po`); if one does, update its `msgstr` instead of duplicating.

- [ ] **Step 4: Compile the catalog**

Run: `python manage.py compilemessages -l es`
If gettext is not installed, use the project's fallback compiler:
`python -c "from portfolio.i18n_compiler import compile_po_to_mo; compile_po_to_mo('locale/es/LC_MESSAGES/django.po', 'locale/es/LC_MESSAGES/django.mo')"`

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest portfolio/tests/test_views_public.py -k spanish -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add locale/es/LC_MESSAGES/django.po locale/es/LC_MESSAGES/django.mo portfolio/tests/test_views_public.py
git commit -m "feat: Spanish translations for the subscribe CTA copy (#116)"
```

---

### Task 5: Full suite, push, PR

**Files:** none new.

- [ ] **Step 1: Run the entire test suite**

Run: `python -m pytest portfolio/tests/ -v`
Expected: everything green, including all pre-existing tests (backward compatibility proof).

- [ ] **Step 2: Push the branch**

```bash
git push -u origin feat/newsletter-cta
```

- [ ] **Step 3: Open the PR** (do NOT merge it — the repo owner merges):

```bash
gh pr create --title "feat: configurable subscribe CTA at the end of blog posts" \
  --body "Closes #116.

- Four optional SiteConfiguration fields (URL + custom copy), dashboard-editable.
- With no URL configured, post pages keep the existing contact CTA (backward compatible, covered by tests).
- With a URL, a subscribe block replaces it: custom copy or generic translatable defaults (EN/ES).
- Button carries data-umami-event=\"newsletter-subscribe\" for the upcoming analytics integration (#117).
- Design spec: docs/superpowers/specs/2026-08-08-newsletter-cta-design.md"
```

- [ ] **Step 4: Report the PR URL and stop.** Deployment to the EC2 (host bind-mount checkout + `docker compose restart web`) and the instance configuration (pasting the real newsletter URL/copy in the dashboard) happen after merge, manually.
