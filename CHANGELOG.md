# Changelog

Meaningful user-facing releases will be recorded here. No MVP release exists yet.

## Unreleased

- Backend checks integration answers (#8): an explicit `aK + b` constant,
  derivative equality and real values on every part of the problem's domain,
  all inside the resource-limited worker. Undecidable answers return a
  retryable inconclusive error instead of a guess. Not yet wired to any route.
- Backend verifies Supabase access tokens (#4): asymmetric JWKS keys only, with
  issuer, audience, expiry and role checks and key rotation. Owner-scoped
  queries for problems, attempts and reveals deny other users' IDs even though
  the backend's database role bypasses RLS. Not yet wired to any route.
- Frontend implements the PracticeLoop design system (#26): Ink tokens, the ten
  components and the six routes (`/`, `/login`, `/dashboard`, `/practice`,
  `/history`, `/profile`) on a temporary mock data layer. No backend or sign-in yet.
- Frontend preview deploys to GitHub Pages from `main` (#28), temporary until
  the Cloudflare deployment (PL-014).
