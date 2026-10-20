# Production checklist (#38)

The twelve gates a release must pass on the preview
(https://practiceloop.pages.dev) before the custom-domain launch (#39). Each item
names the automated check that covers it in CI and the smoke check to repeat on
the deployed preview. Requirements and decisions are in
[PRODUCTION_READINESS_PLAN.md](PRODUCTION_READINESS_PLAN.md).

| # | Gate | Automated check | Preview smoke check |
|---|---|---|---|
| 1 | Routes `/`, `/login`, `/dashboard`, `/practice`, `/history`, `/profile`, `/privacy`, `/s/{token}`, `/shared/{token}`, `/shared`; signed-out visitors are sent from private routes to `/login`; unknown paths show the branded 404 with links home and to practice | `frontend/src/App.test.tsx` | Open `/privacy`, `/shared/x` and `/nowhere` directly (deep links work through the Pages SPA fallback); open `/history` signed out and land on `/login` |
| 2 | The primary CTA is the first hero action, above the fold on desktop and phone, and goes to `/practice` | `App.test.tsx` "puts a practice CTA first" | On a phone, the first button on `/` is visible without scrolling and opens a demo problem |
| 3 | Titles, descriptions, robots, canonical, Open Graph and Twitter tags come from `frontend/src/site.ts`; every page is `noindex` on preview, and login, app, shared, callback and 404 pages stay `noindex` after launch | `frontend/src/site.test.ts` | View source of any page after load: `meta name="robots" content="noindex, nofollow"`; response header `X-Robots-Tag: noindex` |
| 4 | `robots.txt` and, once indexable, `sitemap.xml` are generated from the public route list and `VITE_SITE_URL` | `site.test.ts` "writes crawler files" | `/robots.txt` allows crawling (so crawlers see `noindex`) and names no sitemap |
| 5 | Loading, empty, success and safe error states; a pending request disables its button so a double click sends one request | Page tests (`PracticePage`, `HistoryPage`, `SharedProblemPage`, `ReportProblem`) | Double-click *Check answer*: one attempt appears in history |
| 6 | *Report a problem* stores only problem, category and optional comment, is limited to 5 a minute and 30 an hour per user, and shows safe errors | `backend/tests/test_reports_api.py`, `supabase/tests/isolation.sql`, `ReportProblem.test.tsx` | Signed in, send a report; send six quickly and see the "going a bit fast" message |
| 7 | Skip link, one `h1` per page, labelled controls, visible focus, keyboard use, alternative text and layouts without horizontal scroll at 375 px | Component and App tests; a Chromium + axe-core run of the built site (see below) | Tab from the top of `/`: *Skip to content* appears first; nothing scrolls sideways on a phone |
| 8 | Pages headers from `frontend/public/_headers`: CSP (`script-src 'self'` plus the analytics beacon, no inline script, no eval), `nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, `Permissions-Policy`, COOP; fonts are self-hosted | `site.test.ts` "Pages headers" | `curl -sI https://practiceloop.pages.dev/` shows the headers; the browser console shows no CSP errors while practising and signing in |
| 9 | API: HTTPS only (Caddy redirect and HSTS), exact-origin CORS without wildcards or plain HTTP, strict request models, 4 KB body cap, safe error envelope, security headers on every response | `backend/tests/test_health.py`, `test_practice_api.py`, `scripts/e2e_local.py` | `curl -sI https://92-5-92-72.sslip.io/health` shows `content-security-policy: default-src 'none'...`; an unknown `Origin` gets no CORS header |
| 10 | Cloudflare Web Analytics only when `CF_WEB_ANALYTICS_TOKEN` is set; never on `/auth/*` or share URLs; no email, account ID or answer is ever in a URL; learning metrics stay in Supabase | `frontend/src/analytics.test.ts` | With the token set, the beacon loads on `/` but not on `/s/{token}` |
| 11 | `/privacy` is a draft that describes the real data flows and processors (Supabase, Google, Cloudflare, Oracle) and lists what is undecided instead of inventing it | `App.test.tsx` "serves the privacy draft" | Read `/privacy` against this repository's behaviour |
| 12 | Domains, keys and tokens come from environment configuration; the browser build gets only public values | `scripts/check_repository.py`, Gitleaks, the Preview workflow's public-key check | GitHub variables: `API_BASE_URL`, `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, optional `CF_WEB_ANALYTICS_TOKEN`; no `VITE_SITE_URL` or `VITE_SITE_INDEXABLE` on preview |

## Running the checks

- Frontend: `npm run lint`, `npm run typecheck`, `npm test`, `npm run build` in `frontend/`.
- Backend: `ruff check`, `ruff format --check`, `mypy`, `pytest` in `backend/`;
  database tests with `python scripts/test-db.py` (applies every migration,
  `isolation.sql`, `pytest -m db` and the end-to-end script).
- Browser: build, serve `dist/` with the `/*` headers from `_headers`, and run
  axe-core and a CSP-violation listener on `/`, `/privacy`, `/login`,
  `/practice`, `/shared`, `/s/{token}` and a 404, at 1280 and 375 px. On
  2026-10-20 this found no CSP violations, no axe violations and no horizontal
  overflow, the CTA ended at 517 of 740 px on a phone, and a double-clicked
  *Check answer* sent one request.

## Launch blockers (#39)

These stay open on purpose. Do not fill them with placeholders.

- Custom production domain, then `VITE_SITE_URL`, `VITE_SITE_INDEXABLE=true`,
  HSTS and removing the global `X-Robots-Tag: noindex` from `_headers`.
- Operator's full legal identity and address, a dedicated privacy contact email,
  and the legal basis for each processing purpose, checked by a qualified person.
- Backup setup and retention for launch (the Free plan has no automatic backups).
- Final product name, English hero, CTA and SEO copy, logo, favicon, Apple touch
  icon and Open Graph image (no `og:image` is emitted until then).
- Provisioned production configuration: Cloudflare (domain, Web Analytics site),
  Oracle, Supabase and the Google OAuth consent screen and redirect URLs.
- Any decision to allow accounts for users younger than 16.
