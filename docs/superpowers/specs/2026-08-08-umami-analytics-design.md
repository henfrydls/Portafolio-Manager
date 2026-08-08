# Umami analytics integration — Design

**Date:** 2026-08-08
**Status:** design approved, pending implementation plan
**Issue:** #117

## Context

Two related problems, one root cause:

1. **Dashboard view counts are inflated.** `PageVisitMiddleware` (`portfolio/middleware/base.py`) counts server-side and filters bots only by declared user-agent substrings. Modern crawlers and monitors announce a regular Chrome UA and pass the filter, and reloads by the same visitor are not deduplicated. This is a structural limit of server-side counting: no filter list fixes it.
2. **Umami support is half-wired.** The CSP was opened for an analytics host (#99) but the tracking script was never added to any template, so a deployed Umami instance collects nothing. The analytics host is also hardcoded in the CSP settings, which a generic product cannot assume.

Client-side counting solves (1): most bots never execute JavaScript, and Umami additionally filters known bots and deduplicates visitors. The integration must be instance-agnostic — any self-hosted or cloud Umami works; nothing is tied to a particular domain.

## Phases

Each phase works standalone, ships in its own PR, and carries its own tests.

### Phase 1 — Tracking script

- `SiteConfiguration` fields: `umami_script_url` (`URLField`, blank), `umami_website_id` (`CharField(64)`, blank), plus dashboard form/template fields (same pattern as the subscribe CTA config).
- `base.html` renders `<script defer src="{umami_script_url}" data-website-id="{umami_website_id}">` only when **both fields are set and `request.user` is not authenticated** — the owner's own dashboard sessions and page previews never pollute the data.
- CSP: derive the allowed analytics host for `script-src`/`connect-src` from the configured script URL (or an env var), replacing the hardcoded domain.

### Phase 2 — Real numbers in the dashboard

- New service `UmamiClient` (`portfolio/services/`): authenticates against the Umami API via `POST /api/auth/login` with a dedicated account's username/password (stored in `SiteConfiguration`, password widget), caches the returned JWT alongside the stats, and re-authenticates on 401. Fetches website stats (pageviews, visitors), top pages, referrers, countries and events for 24h / 7d / 30d ranges.
- **Caching:** Django cache, 10–15 min TTL. **Fail-soft:** any client error (timeout, auth failure, Umami down) renders an "analytics unavailable" notice; the rest of the dashboard keeps working. No exception ever reaches the user.
- Analytics page: the Umami section becomes the primary "real visits" display. The existing `PageVisit` section stays but relabeled: "HTML requests (includes browser-UA bots)". Removing `PageVisitMiddleware` is deliberately out of scope — decide later with accumulated Umami data.

### Phase 3 — Events

- `data-umami-event` attributes on: the existing share buttons in `blog_detail.html`, contact modal open/submit, outbound profile links (GitHub/LinkedIn), and the subscribe CTA (#116, already specified).
- Scroll-depth events on post pages (25/50/75/100%), emitted only when the tracking script is configured.

## What Umami cannot see

Link-preview fetches (LinkedIn/WhatsApp bots generating a preview card) never execute JS, so they are invisible to Umami. That signal — "someone shared the link" — remains in the server logs. Server-side log analysis stays complementary, not redundant.

## Error handling

All failure paths live in `UmamiClient` and degrade to the "analytics unavailable" state. The tracking script itself is fire-and-forget in the browser; a blocked or failed script load has no effect on the page.

## Tests

1. Script rendering: absent without config; absent for authenticated users; present for anonymous users with config.
2. `UmamiClient`: success, timeout, auth failure → fail-soft result; all HTTP mocked.
3. Dashboard view with mocked client: stats rendered; unavailable state rendered.
No real API calls in CI.

## Out of scope

- Removing `PageVisitMiddleware`.
- Multi-provider analytics abstraction (Plausible, GA, etc.).
- UTM link conventions (instance-level publishing practice, not product code).
- Instance provisioning (creating the website entry in a Umami server, tokens): deployment configuration, not code.
