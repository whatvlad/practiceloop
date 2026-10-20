# Changelog

Meaningful user-facing releases will be recorded here. No MVP release exists yet.

## Unreleased

- Definite integrals (#36, part 2): most practice cells now also offer definite
  integrals with clean bounds and exact values such as `e - 2` or `3 ln(4/3)`.
  Their answer is one number with no `+ C`; bounds never touch a singularity.
  Constant-omission statistics leave definite answers out.
- Signed-in practice offers every approved topic and level (#36, part 1): all
  five topics at levels 1–5, with integration by parts from level 3. The answer
  checker grades the new substitution, parts, rational and trigonometric problems
  on every part of their domain. Definite integrals, mixed practice and mistake
  feedback are still to come.
- Backend saves practice for signed-in learners (#10): generating a problem stores
  it with its private solution, every checked answer is stored (including invalid
  ones and a missing-constant flag), and reveals set their flags. Retries with the
  same idempotency key never duplicate work. The app itself still uses the
  untracked preview until #11.
- Hosted Supabase two-user isolation check passed with two real Google accounts; #3 done.
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
