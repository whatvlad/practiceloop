# PracticeLoop production roadmap

Status: approved roadmap; publication tracked by GitHub Issue #31.

This document records the agreed staged path from the development preview to a
public launch. GitHub Issue #30 is the authoritative tracker. This roadmap is
not permission to push branches, deploy services, merge pull requests or modify
external accounts; each Issue still requires an accountable human and the
approvals defined in `AGENTS.md`.

## Required reading

Read these files before planning, publishing or implementing any roadmap item:

1. `AGENTS.md`
2. `docs/agents/WORKFLOW.md`
3. `docs/agents/TASK_PROTOCOL.md`
4. `docs/agents/REVIEW_PROTOCOL.md`
5. `docs/agents/HANDOFF.md`
6. `docs/production/PRODUCTION_READINESS_PLAN.md`
7. `docs/intent/PROBLEM_GENERATION.md`
8. `docs/intent/CONTENT_STYLE.md`

The final three files are the approved product-intent sources produced during
the product-owner interview. Do not replace them with assumptions or compress
them into a single implementation task.

## Repository state when the roadmap was published

- Repository: `whatvlad/practiceloop`.
- Current public preview: <https://whatvlad.github.io/practiceloop/>.
- PR #16 is merged. Issue #1 still requires status reconciliation against its
  remaining acceptance criteria.
- The design system and GitHub Pages preview were delivered by Issues #26 and
  #28. GitHub Pages remains a temporary mock-data preview.
- GitHub Issues #30 through #39 contain this roadmap, its preparation tasks and
  its seven implementation stages.
- Production, generator and content-style documents belong to Issue #31.
  Graphify tooling belongs to Issue #32 and must not be mixed into #31.

At the start of a new chat, inspect the real state instead of relying on this
snapshot:

```bash
git status --short --branch
git remote -v
git fetch origin --prune
```

Then inspect the current GitHub Issues, open pull requests, labels, default
branch and dependencies. If the existing worktree is dirty, create a separate
worktree or clone from current `origin/main`. Do not move or discard the local
changes merely to obtain a clean branch.

## Confirmed product direction

PracticeLoop addresses the lack of useful mathematics practice. The first beta
focuses on integration for secondary-school and university learners, with other
mathematics topics possible later. The beta is international and English-first.
The code should make additional languages practical later without building a
full localization system now.

The planned production architecture is:

- React, TypeScript and KaTeX frontend on Cloudflare Pages;
- FastAPI, Python and SymPy API on Oracle Cloud Free Tier;
- Supabase PostgreSQL and Auth;
- Google login for the MVP; Apple login is deferred;
- Cloudflare Web Analytics plus first-party learning statistics in Supabase.

Development and preview hosts remain `noindex`. Search indexing begins only
after the owner approves a custom production domain and the public-launch gate
passes.

## Planned Graphify policy

Graphify exists only to help agents understand and change the repository with
less repeated full-repository reading. It is not part of the PracticeLoop
product or production architecture.

Issue #32 owns the publication of these planned repository assets:

- `.codex/skills/graphify/` for the project-local agent skill;
- `.codex/hooks.json` when installed by Graphify;
- `scripts/setup-graphify.sh` for reproducible local installation and updates;
- `graphify-out/graph.json` and the agreed team outputs;
- `AGENTS.md` instructions that require scoped graph queries first.

For a codebase question, when `graphify-out/graph.json` exists:

```bash
.local/graphify-venv/bin/graphify query "<specific question>" --budget 2500
```

Use the executable recorded by Graphify or an available `graphify` executable if
the repository-local virtual environment does not exist. Use `path` for a
relationship and `explain` for one concept. Verify relevant source locations
after the graph narrows the search. After code changes, update the graph:

```bash
.local/graphify-venv/bin/graphify update .
```

If Graphify cannot run, report that fact and continue with ordinary repository
tools. A missing graph must never block product work. Do not add Graphify to
frontend or backend dependencies, production images, CI runtime services, API
requests or deployed assets.

## GitHub Issue structure

Issue #30 is the parent tracker. It links every preparation task and
implementation stage below, preserves their dependency order, and requires each
implementation stage to end with a usable, tested deployment or feature slice.
The source documents inform the work; they are not implementation boundaries.

Do not create GitHub Milestones initially. Add them only if a stage later needs
several independently owned Issues. Use the exact Issue fields required by
`docs/agents/TASK_PROTOCOL.md`. Before claiming work, use `Agent: none`,
`Human owner: Unassigned`, and `Status: Backlog`; never invent owners.

### Issue #31: publish approved intent documents

Suggested title: `Document production, generator, and content-style decisions`

- Type: Documentation
- Priority: P0
- Branch: `docs/issue-31-product-intent`
- Dependencies: none
- Scope: publish the three approved source documents and this roadmap;
  add navigation links only where appropriate.
- Exclusions: application code, deployment, external-service configuration and
  changes to the original MVP source of truth.
- Acceptance: all documents are in English, internally consistent, linked from
  appropriate repository navigation, and clearly distinguish confirmed choices
  from unresolved decisions.

### Issue #32: publish Graphify agent tooling

Suggested title: `Add Graphify-assisted repository navigation for agents`

- Type: Infrastructure
- Priority: P1
- Branch: `feature/issue-32-graphify-agent-tooling`
- Dependencies: Issue #31
- Scope: project-local skill and hooks, reproducible setup script, selected
  shared graph outputs, ignore rules and the single Graphify section in
  `AGENTS.md`.
- Exclusions: application dependencies, runtime behavior, production images,
  deployed services and product analytics.
- Acceptance: a fresh developer can run the setup, an agent is instructed to
  query the graph before broad source scans, a scoped query works, source code
  remains authoritative, and normal work can continue when Graphify is absent.

Review Graphify-generated output before committing it. Do not commit machine
specific paths, private data, caches, cost history or secrets. Confirm the
current Graphify team-workflow guidance before deciding the exact generated
files to track.

## Implementation stages

The stages below are ordered dependencies. Each stage receives its own Issue and
pull request unless it is deliberately decomposed after review. Do not begin a
dependent stage merely because its Issue exists; its dependency must meet the
repository's definition of Done.

### Issue #33: working preview infrastructure

Suggested title: `Deploy a connected Cloudflare Pages and Oracle preview`

- Type: Infrastructure
- Priority: P0
- Branch: `feature/issue-33-preview-deployment`
- Dependencies: Issues #31 and #32
- Deliver a frontend preview on a free `*.pages.dev` address.
- Deploy FastAPI on Oracle Cloud Free Tier.
- Connect the frontend to the API through environment configuration.
- Provide a working HTTPS health check and verify the deployed `/health` path.
- Configure preview CORS, safe environment handling, basic deployment
  documentation and rollback/recovery instructions.
- Keep GitHub Pages only until the Cloudflare preview is verified; document the
  transition instead of silently removing a working preview.
- Keep every preview host `noindex`.
- Do not add Supabase, login, a purchased custom domain or public indexing.

Acceptance: the deployed frontend loads over HTTPS, reaches the deployed API,
shows a safe failure state when the API is unavailable, and automated builds and
tests still pass.

### Issue #34: usable core integration practice

Suggested title: `Deliver the core reverse-generated integration practice flow`

- Type: Feature
- Priority: P0
- Branch: `feature/issue-34-core-integration-practice`
- Dependencies: Issue #33
- Implement the backwards generation model in
  `docs/intent/PROBLEM_GENERATION.md`.
- Cover pedagogically clean power, exponential and trigonometric families plus
  simple substitution at difficulty levels 1 and 2.
- Generate from a clean antiderivative, differentiate symbolically, apply only
  allowed equality-preserving transformations, and reject invalid candidates.
- Verify mathematical equivalence, real-domain constraints and clean visible
  values. Difficulty must come from structure, not arbitrary large numbers.
- Deliver the connected frontend flow for generating, displaying, answering and
  receiving feedback on a problem.
- Treat this as an untracked preview flow; account limits and persistent history
  arrive in Issue #35.
- Add the typed English educational-template catalogue and deterministic
  STE-inspired development checker described in `docs/intent/CONTENT_STYLE.md`.
  Run the same checker in CI. Do not perform runtime rewriting and do not claim
  formal ASD-STE100 compliance.

Acceptance: a learner can complete supported exercises through the deployed
preview; generated exercises satisfy tested math invariants; invalid domains and
ugly values are rejected; content checks meet the internal 80/100 threshold;
loading, duplicate-submit prevention and safe errors are present.

### Issue #35: accounts, private history and learning statistics

Suggested title: `Add Supabase Google auth and private learning history`

- Type: Feature
- Priority: P0
- Branch: `feature/issue-35-auth-learning-history`
- Dependencies: Issue #34
- Add Supabase PostgreSQL and Google OAuth. Apple login remains deferred.
- Allow one untracked anonymous demo problem; require login for further tracked
  practice, history and statistics.
- Store only the data defined in the production-readiness plan, including topic,
  difficulty, generator version, submission, correctness, timing and hint or
  solution use.
- Track omission of the arbitrary integration constant separately from ordinary
  incorrect answers and expose its count, rate and trend.
- Add a minimal private profile and history UI.
- Enforce RLS, backend ownership checks and verified JWT claims. Never expose a
  Supabase service-role key to the browser.
- Add self-service account deletion with explicit confirmation. Delete active
  data immediately; backups expire within at most 30 days; only irreversible
  aggregates may remain.

Acceptance: Google login works in the preview, anonymous work is not persisted,
users cannot read or change another user's data, history and `+C` statistics are
correct, deletion works, and database isolation tests pass.

### Issue #36: advanced integration generator

Suggested title: `Expand the generator to advanced integration methods`

- Type: Feature
- Priority: P1
- Branch: `feature/issue-36-advanced-integrals`
- Dependencies: Issue #35
- Add integration by parts, partial fractions, preparatory transformations and
  trigonometric identities for difficulty levels 3 through 5.
- Keep one declared primary method with only compatible auxiliary operations.
- Add template-declared common mistakes and targeted feedback only when a
  submitted expression unambiguously matches a known mistake.
- Support definite and indefinite integrals with their different `+C`, bound,
  singularity and clean-result rules.
- Support practice by topic and transparent weighted mixed practice.
- Accept equivalent valid answers and alternative valid solution methods.
- Adaptive selection remains deferred until enough real learning data exists.

Acceptance: every new family has invariant, domain, rejection, equivalence and
mistake-diagnosis tests; levels 3–5 are structurally harder without ugly values;
deployed preview behavior remains usable.

### Issue #37: privacy-safe problem sharing

Suggested title: `Share generated problems by link and short code`

- Type: Feature
- Priority: P1
- Branch: `feature/issue-37-problem-sharing`
- Dependencies: Issue #36
- Use a cryptographically random opaque token plus a user-friendly short code.
  Do not use a predictable content hash as an access token.
- Share only problem statement, topic and difficulty.
- Never share the owner's answer, result, statistics or correct solution.
- Expire shares after 90 days and let the owner revoke them earlier.
- Mark shared pages `noindex` and provide safe expired/revoked/not-found states.
- Rate-limit lookup and creation where appropriate.

Acceptance: link and code lookup work in the preview, expiration and revocation
are tested, private data never appears in responses or page source, and crawlers
are instructed not to index shared pages.

### Issue #38: production readiness on the preview domain

Suggested title: `Complete the production-readiness gate on preview`

- Type: Feature
- Priority: P0
- Branch: `feature/issue-38-production-readiness`
- Dependencies: Issue #37
- Implement the full must-have scope in
  `docs/production/PRODUCTION_READINESS_PLAN.md` that does not require the final
  domain or unresolved legal/brand values.
- Include routes, custom 404, above-the-fold CTA, route metadata, Open Graph and
  Twitter templates, provisional icons if an approved source asset exists,
  loading/error/empty states, reporting, accessibility, responsive behavior,
  image optimization and baseline security headers.
- Configure Cloudflare Web Analytics without sending email addresses, account
  identifiers or raw answers. Keep first-party learning metrics in Supabase.
- Do not install another analytics provider without owner approval.
- Do not add a cookie banner unless an introduced service actually requires
  consent.
- Prepare the Privacy Policy from actual data flows and processors, but do not
  invent the operator's legal name, address or contact details. Missing legal
  identity remains a launch blocker.
- Keep preview deployments and all private routes `noindex`.

Acceptance: the twelve-item production checklist is verified on preview;
accessibility and responsive checks pass; async operations prevent duplicate
requests; security headers and API error handling are tested; unresolved launch
values remain explicit rather than fabricated.

### Issue #39: custom-domain public launch

Suggested title: `Launch PracticeLoop on the approved production domain`

- Type: Infrastructure
- Priority: P0
- Branch: `feature/issue-39-public-launch`
- Dependencies: Issue #38 and every launch blocker below
- Connect the owner-approved custom domain through Cloudflare.
- Confirm the Polish operator's full legal identity and dedicated privacy/contact
  email with a qualified person; update the Privacy Policy accordingly.
- Approve final product name, English CTA and SEO copy, logo, favicon and Open
  Graph image.
- Set the production base URL through environment configuration.
- Emit correct canonical URLs, production `robots.txt` and `sitemap.xml`.
- Remove `noindex` only from approved public, indexable routes. Keep login,
  account, practice, history, profile, shared problems and error pages out of the
  index as specified by the production plan.
- Verify HTTPS, DNS, redirects, OAuth callback URLs, CORS, analytics privacy,
  backups, secret handling and rollback on the real domain.

Acceptance: the approved domain serves the tested release over HTTPS, canonical
and crawler files use that domain, only approved public pages are indexable,
OAuth and API calls work, legal/operator data is real and reviewed, and the
owner explicitly authorizes launch.

## Launch blockers that must not be guessed

- exact custom production domain;
- operator's complete legal identity and address;
- dedicated privacy/contact email;
- final logo, favicon and Open Graph source image;
- final English hero, CTA and SEO copy;
- provisioned Cloudflare, Oracle, Supabase and Google OAuth configuration;
- any legal decision that permits accounts for users younger than 16.

Ask the owner when a stage reaches one of these decisions. Do not create fake
legal text, placeholder operator data, hard-coded domains, secrets or API keys.

## Pull-request and delivery rules

For every task:

1. Check live Issue and PR state and claim exactly one scoped Issue.
2. Branch from current `origin/main` in a clean isolated worktree.
3. Record the real human owner and active agent; never invent either.
4. Implement only the Issue scope and preserve unrelated work.
5. Run the relevant typecheck, lint, tests, build, math invariants, database
   isolation tests and secret scan.
6. Update Graphify after code changes and inspect the generated diff.
7. Open a PR that links the Issue and records verification and rollout risks.
8. Obtain independent review and at least one independent human approval.
9. Never merge the agent's own PR and never force-push.

After each implementation stage, verify the deployed result before beginning
the next dependent stage. A local build or open PR alone does not make a stage
Done.

## Explicitly deferred work

- final visual redesign and broader UX work beyond production blockers;
- Apple login;
- additional languages and non-integration mathematics topics;
- adaptive problem selection until sufficient real statistics exist;
- monetization;
- PWA/offline support;
- Sentry or another external error tracker;
- Turnstile unless actual abuse demonstrates the need.

## Current execution order

Complete Issue #31, then #32. Issue #33 can proceed after both preparation
tasks are Done. Issues #34 through #39 form a strict dependency chain. Keep
Issue #30 open as the tracker until the public-launch criteria in #39 are met.
Always inspect live Issue and pull-request state before starting work because
this document is a versioned plan, not a synchronization mechanism.
