# PracticeLoop production readiness plan

Status: approved requirements draft; implementation not started.

This document records the production-readiness audit and the decisions made with
the product owner. It intentionally does not invent unresolved legal, branding,
content, or infrastructure details.

## Product decisions

- PracticeLoop addresses the shortage of useful mathematics practice. The first
  beta covers integration, while the product may later cover other topics.
- The initial audience includes secondary-school and university students in an
  international, English-language beta.
- The architecture should make later languages practical without building a full
  localization system before a second language exists.
- An anonymous visitor may solve one untracked demo problem. Further problems,
  history, and statistics require Google authentication through Supabase.
- Apple authentication is deferred.
- Accounts are initially limited to users aged 16 or older, pending legal review
  of support for younger users.
- The beta is free and has no advertising, payments, subscriptions, newsletter,
  or contact form.
- The planned stack is Cloudflare Pages, FastAPI on Oracle Free Tier, and
  Supabase Auth/PostgreSQL.
- The current GitHub Pages address is a development preview:
  <https://whatvlad.github.io/practiceloop/>.
- Development and preview hosts stay `noindex`; indexing starts only after a
  custom production domain is approved.

## Must-have before production

### Routing and public pages

- Add routes for `/`, `/login`, `/dashboard`, `/practice`, `/history`,
  `/profile`, `/privacy`, and `/shared/:token`.
- Add a branded 404 route with links back to the home and practice pages.
- Configure an SPA fallback for Cloudflare Pages.
- Protect private routes with the Supabase session.

### Landing page and CTA

- Place the primary CTA above the fold and link it to `/practice`.
- Let an anonymous visitor solve one problem without creating an account or
  persistent learning history.
- Require login for additional tracked problems and user statistics.
- Final hero copy, CTA wording, visual design, and UI remain deferred.

### SEO and sharing metadata

- Give every important public page a unique title and description.
- Generate canonical, Open Graph, and Twitter/X metadata from a shared site
  configuration.
- Mark login, dashboard, practice, history, profile, shared problems, and 404 as
  `noindex`.
- Generate `robots.txt` and `sitemap.xml` from the public route list and approved
  base URL.
- Keep preview deployments `noindex` and enable indexing only on the approved
  custom domain.
- Prepare favicons, an Apple touch icon, and an Open Graph image after the source
  logo is identified.

### Authentication and personal data

- Use Google OAuth through Supabase. Do not implement Apple login in the MVP.
- Make the display name optional, editable, and removable.
- Keep profiles and learning history private with RLS and backend ownership
  checks.
- Keep the service-role key on the backend only.
- Provide self-service account deletion with explicit confirmation.
- Delete active account data immediately; allow backups to expire within at
  most 30 days. Only irreversibly aggregated statistics may remain.
- Do not automatically link identities from different login providers.

### Practice flow

- Add loading, empty, success, and error states for asynchronous operations.
- Disable submissions while a request is pending to prevent duplicate attempts.
- After a wrong answer, allow another attempt, a hint, or an explicit solution
  reveal.
- For authenticated users, record the problem/topic, difficulty, generator
  version, submitted answer, correctness, timing, and hint/solution use.
- Do not persist an anonymous visitor's answer or result.

### Shared problems

- Share only the problem statement, topic, and difficulty.
- Never expose the owner's answer, result, statistics, or the correct solution.
- Use an opaque random token and a short code, not a predictable content hash.
- Expire a shared problem after 90 days and let its owner revoke it earlier.
- Mark shared problem pages `noindex`.

### Problem reports

- Add a `Report a problem` action.
- Store the problem identifier, an error category, and an optional comment.
- Do not require extra personal information.
- Rate-limit submissions and display safe error feedback.

### Privacy and analytics

- Publish a policy that describes the actual operator, data, purposes,
  processors, retention, deletion, and user rights.
- Cover Supabase, Google OAuth, Cloudflare Web Analytics, and Oracle hosting.
- Do not publish placeholder or invented operator details.
- Use Cloudflare Web Analytics for anonymous traffic and performance data.
- Store first-party learning/product metrics in Supabase.
- Never send email addresses, account identifiers, or raw answers to Cloudflare.
- Do not add a consent banner unless optional cookies or consent-dependent tools
  are introduced.

### Security, accessibility, and deployment

- Allow CORS only from known origins and require HTTPS outside local development.
- Add an appropriate CSP and baseline security headers.
- Validate all trust boundaries and return safe API errors.
- Apply backend rate limits to anonymous generation. Add Turnstile only if real
  abuse warrants it.
- Use semantic HTML, correct heading order, labelled controls, keyboard support,
  visible focus states, and useful alternative text. Decorative images use an
  empty `alt`.
- Keep domains, secrets, and API keys in environment configuration.
- Use Cloudflare Pages for the frontend, Oracle for FastAPI, and Supabase for
  Auth/PostgreSQL.

## Recommended

- Add a React error boundary and route/API error views.
- Use skeletons only for waits where they improve comprehension; use a simple
  busy indicator for short operations.
- Test routing, metadata, auth guards, deletion, sharing, reporting, and RLS.
- Add appropriate Schema.org data after the organization and public copy are
  final.
- Measure Core Web Vitals and lazy-load non-critical large assets.
- Centralize user-facing strings so a second language can be added later without
  introducing a localization framework now.
- Document secret rotation, backups, least-privilege access, audit logging, and
  the Irish contractor's production access.

## Optional or deferred

- Apple login.
- Sentry or another external error tracker.
- Cloudflare Turnstile.
- PWA/offline support.
- Additional languages and mathematics topics.
- Adaptive problem selection and richer progress dashboards.
- Monetization.

## Expected implementation surface

Existing files likely to change:

- `.env.example`
- `frontend/package.json` and `frontend/package-lock.json`
- `frontend/index.html`
- `frontend/src/main.ts`
- `backend/app/main.py`
- `backend/pyproject.toml` and `backend/requirements.txt`
- Supabase schema through a new migration if the initial migration was already
  applied
- `README.md` and relevant architecture/deployment documentation

Likely new files:

- `frontend/src/App.tsx`
- `frontend/src/routes.tsx`
- `frontend/src/pages/*.tsx`
- focused files under `frontend/src/components/` and `frontend/src/lib/`
- `frontend/src/styles.css`
- public metadata, icon, redirect, and header files under `frontend/public/`
- focused FastAPI routes/services and their tests
- frontend routing/auth/metadata tests and Supabase RLS tests

The implementation should stay flat and use native framework/platform features
before adding dependencies or abstractions.

## Unresolved production blockers

- Final visual design and UI.
- Approved English hero, CTA, and SEO copy.
- Source logo and Open Graph image.
- Custom production domain.
- Full legal identity and contact details of the Polish operator.
- Dedicated privacy/contact email.
- Provisioned Cloudflare, Oracle, Supabase, and Google OAuth configuration.
- Independent verification that the GitHub Pages build matches this repository.

## Verification and publication rules

- Run frontend typecheck, lint, tests, and build.
- Run backend format/lint, typecheck, tests, and relevant database isolation tests.
- Inspect the final diff and run the repository's secret scan.
- Do not commit, push, deploy, merge, or change hosted services without the
  owner's explicit instruction.
