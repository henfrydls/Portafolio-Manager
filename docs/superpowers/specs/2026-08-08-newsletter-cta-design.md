# End-of-post subscribe CTA — Design

**Date:** 2026-08-08 (amended same day: made product-generic, no personal branding in code)
**Status:** design approved, pending implementation plan

## Goal

Readers who finish a post are the most engaged visitors a site gets. Give site owners a configurable subscribe block at the end of each blog post pointing to wherever their newsletter lives (LinkedIn, Substack, Mailchimp, Kit, etc.), without hardcoding any instance-specific branding into the product.

## Decisions

1. **Inline block, not a modal/popup.** Popups interrupt reading and Google penalizes intrusive interstitials on mobile.
2. **Destination and copy are instance configuration** (`SiteConfiguration`), editable from the dashboard without redeploying. The product ships with generic, translatable default copy.
3. **Backward compatible.** With no `newsletter_url` configured, the existing contact CTA ("Enjoyed this post?") renders exactly as today. When configured, the subscribe block takes its place; contact remains reachable through the author-bio "Get in touch" link right above.
4. **Empty URL = feature off.** No extra boolean flag.

## Changes

| # | File | Change |
|---|---|---|
| 1 | `portfolio/models.py` | Four fields on `SiteConfiguration`: `newsletter_url` (`URLField`, blank), `newsletter_title` (`CharField(100)`, blank), `newsletter_description` (`CharField(255)`, blank), `newsletter_button_text` (`CharField(50)`, blank). One migration. |
| 2 | `portfolio/forms/config.py` | Add the four fields to `SiteConfigurationForm` with matching widgets (`URLInput`/`TextInput`, class `form-control`). |
| 3 | `templates/portfolio/admin/site_configuration.html` | New fields in the dashboard form. |
| 4 | `templates/portfolio/includes/subscribe_cta.html` | New component. Renders only when `site_config.newsletter_url` is set. Each text falls back to generic `{% trans %}` copy when its field is empty. |
| 5 | `templates/portfolio/blog_detail.html` | Conditional: if `newsletter_url` is set, include the component; otherwise keep the existing `post-contact-cta` block (lines 213–222) unchanged. The component reuses the existing CTA CSS classes (`post-contact-cta`, `cta-content`, `cta-title`, `cta-text`, `cta-button`); no new CSS. |

`site_config` is already available in every template through the context processor (`portfolio/context_processors.py`); no view changes needed.

## Generic default copy (translatable via `{% trans %}`)

| Field | Default |
|---|---|
| Title | Newsletter |
| Description | Get notified when new posts are published. |
| Button | Subscribe |

Deliberately destination-neutral (works whether the newsletter lives on LinkedIn, email, or elsewhere).

## Analytics hook

The button carries `data-umami-event="newsletter-subscribe"` (inert unless an analytics script is installed — see the Umami integration spec) and uses `target="_blank" rel="noopener"`.

## Error handling

No new backend and no external calls, so no error states. With `newsletter_url` empty the block simply does not render.

## Tests

1. No `newsletter_url` → the contact CTA renders, no subscribe block (backward compatibility).
2. `newsletter_url` set, copy fields empty → block renders with the generic copy and the correct `href`.
3. Copy fields set → custom copy is rendered verbatim.
4. `SiteConfigurationForm` saves the four fields.

## Out of scope

- Site i18n bug (#115): until fixed, visitors see the default language regardless of the switcher.
- Per-category/per-series destinations (add when a second series actually exists).
- Scroll-triggered slide-in (possible phase 2; measure the inline block first).
- Newsletter provider integrations (Kit — issue #11).
